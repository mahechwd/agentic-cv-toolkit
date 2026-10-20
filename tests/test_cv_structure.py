import json
from pathlib import Path
import unittest

from scripts.cv_latex import LatexSyntaxError
from scripts.cv_source import SourceSnapshot
from scripts.cv_structure import extract_structure

FIXTURES = Path(__file__).parent / 'fixtures/parser'


class StructureTests(unittest.TestCase):
    def extract(self, content, preamble=''):
        source = SourceSnapshot(Path('/synthetic/main.tex'),
                                (preamble + '\\begin{document}\n' + content + '\n\\end{document}').encode())
        return source, extract_structure(source)

    def test_reference_structure_matches_contract_without_text_rendering(self):
        source = SourceSnapshot.read(FIXTURES / 'synthetic.tex')
        result = extract_structure(source)
        expected = json.loads((FIXTURES / 'expected.json').read_text())
        self.assertEqual(result.source_sha256, expected['source_sha256'])
        def without_text(value):
            if isinstance(value, dict):
                return {key: without_text(child) for key, child in value.items() if key != 'text'}
            if isinstance(value, list):
                return [without_text(child) for child in value]
            return value
        # Skills and contact rendering are task 5; structural entries are exact now.
        self.assertEqual(list(result.sections[:3]), without_text(expected['sections'][:3]))
        self.assertIn('Languages', result.sections[3]['items'][0]['raw_latex'])
        self.assertTrue(result.header)

    def test_duplicate_names_preserve_order_and_unique_ids(self):
        entry = r'\resumeSubheading{Engineer}{2025}{Example}{Remote}\resumeItem{}'
        _, result = self.extract(r'\section{Experience}' + entry + entry + r'\section{Other}' + entry)
        entries = [e for s in result.sections for e in s['items']]
        self.assertEqual([e['id'] for e in entries], ['s1.e1', 's1.e2', 's2.e1'])
        self.assertEqual([e['heading']['fields'][2]['raw_latex'] for e in entries], ['Example'] * 3)
        self.assertTrue(all(e['items'][0]['body_latex'] == '' for e in entries))

    def test_subroles_remain_under_parent_and_new_entry_resets_parent(self):
        _, result = self.extract(r'''\section{Experience}
\resumeSubheading{Company}{2020 -- 2025}{}{}
\resumeSubSubheading{Engineer}{2020}\resumeItem{First}
\resumeSubSubheading{Senior Engineer}{2023}\resumeItem{Second}
\resumeSubheading{Other Company}{2025}{}{}\resumeItem{Third}''')
        entries = result.sections[0]['items']
        self.assertEqual(len(entries), 2)
        self.assertEqual([e['id'] for e in entries[0]['items']], ['s1.e1.e1', 's1.e1.e2'])
        self.assertEqual(entries[0]['items'][1]['items'][0]['body_latex'], 'Second')
        self.assertEqual(entries[0]['span']['end_byte'], entries[0]['items'][-1]['span']['end_byte'])
        self.assertEqual(entries[1]['items'][0]['body_latex'], 'Third')

    def test_preamble_and_comments_do_not_create_entries(self):
        _, result = self.extract('\\section{Projects}\n% \\resumeItem{hidden}\n',
                                r'\newcommand{\example}{\section{Fake}\resumeItem{Fake}}')
        self.assertEqual(len(result.sections), 1)
        self.assertEqual(result.sections[0]['items'], [])

    def test_arguments_allow_comments_and_nested_formatting(self):
        source, result = self.extract(r'''\section{Projects}
\resumeProjectHeading % comment
{\textbf{Démo} $|$ Python}{}
\resumeItem{A \textbf{\emph{nested}} result.}''')
        entry = result.sections[0]['items'][0]
        bullet = entry['items'][0]
        self.assertEqual(bullet['body_latex'], r'A \textbf{\emph{nested}} result.')
        self.assertEqual(source.slice_text(bullet['body_span']['start_byte'], bullet['body_span']['end_byte']), bullet['body_latex'])
        self.assertEqual(entry['heading']['fields'][1]['raw_latex'], '')

    def test_wrappers_and_empty_section(self):
        _, result = self.extract(r'''\section{Experience}\resumeSubHeadingListStart
\resumeSubheading{Engineer}{2025}{Example}{Remote}
\resumeItemListStart\resumeItem{A}\resumeItemListEnd
\resumeSubHeadingListEnd\section{Projects}''')
        self.assertEqual(len(result.sections[0]['items'][0]['items']), 1)
        self.assertEqual(result.sections[1]['items'], [])

    def test_unknown_content_is_retained_but_hidden_structure_rejected(self):
        _, result = self.extract(r'\section{Skills}\unknown{Useful content}')
        self.assertEqual(result.sections[0]['items'][0]['raw_latex'], r'\unknown{Useful content}')
        with self.assertRaises(LatexSyntaxError) as caught:
            self.extract(r'\section{Skills}\unknown{\resumeItem{Hidden}}')
        self.assertEqual(caught.exception.code, 'nested_structure')

    def test_invalid_structures_fail_with_locations(self):
        cases = [
            (r'\resumeItem{x}', 'orphan_content'),
            (r'\resumeSubheading{a}{b}{c}{d}', 'heading_without_section'),
            (r'\section{Experience}\resumeSubSubheading{a}{b}', 'orphan_subheading'),
            (r'\section{Experience}\resumeSubheading{a}{b}', 'missing_argument'),
            (r'\section*{Experience}', 'missing_argument'),
            (r'\section{Experience}\resumeItemListEnd', 'list_mismatch'),
            (r'\section{Experience}\resumeSubHeadingListStart', 'unclosed_container'),
            (r'\begin{itemize}\end{center}', 'environment_mismatch'),
            (r'\resumeSubHeadingListStart\begin{itemize}\resumeSubHeadingListEnd\end{itemize}', 'list_mismatch'),
            (r'\begin{verbatim}text\end{verbatim}', 'unsupported_environment'),
            (r'\section{Experience}\input{other}', 'unsupported_structure'),
            (r'\iffalse\section{Hidden}\fi', 'unsupported_structure'),
            (r'\begin{itemize}\section{Experience}\end{itemize}', 'section_in_container'),
        ]
        for content, code in cases:
            with self.subTest(content=content), self.assertRaises(LatexSyntaxError) as caught:
                self.extract(content)
            self.assertEqual(caught.exception.code, code)
            self.assertGreaterEqual(caught.exception.span['start_byte'], 0)

    def test_document_boundaries(self):
        for text in ('', r'\begin{document}', r'\end{document}\begin{document}',
                     r'\begin{document}\end{document}extra',
                     r'\begin{document}\begin{document}\end{document}'):
            with self.subTest(text=text), self.assertRaises(LatexSyntaxError):
                extract_structure(SourceSnapshot(Path('/synthetic/main.tex'), text.encode()))


if __name__ == '__main__':
    unittest.main()
