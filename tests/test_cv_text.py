import json
from pathlib import Path
import unittest

from scripts.cv_latex import LatexSyntaxError
from scripts.cv_source import SourceSnapshot
from scripts.cv_text import TextReader, parse_cv

FIXTURES = Path(__file__).parent / 'fixtures/parser'


class ReadableTests(unittest.TestCase):
    def text(self, value):
        source = SourceSnapshot(Path('/synthetic/main.tex'), value.encode())
        return TextReader(source).text(source.span(0, len(source.raw)), single_line=False)

    def test_complete_contract_matches_without_changing_expected_fixture(self):
        source = SourceSnapshot.read(FIXTURES / 'synthetic.tex')
        result = parse_cv(source)
        expected = json.loads((FIXTURES / 'expected.json').read_text())
        expected['source_path'] = str(source.path)
        self.assertEqual(result, expected)
        self.assertEqual(result['readable_text'], (FIXTURES / 'expected.txt').read_text())

    def test_formatting_symbols_and_link_labels(self):
        self.assertEqual(self.text(r'\textbf{A \emph{nested}} 25\% \& x\_y $\sim$2 -- 3'),
                         'A nested 25% & x_y ∼2 – 3')
        self.assertEqual(self.text(r'\href{https://example.com}{Example} $|$ \url{https://example.com/a--b~c}'),
                         'Example | https://example.com/a--b~c')

    def test_comments_and_tex_control_word_spacing(self):
        self.assertEqual(self.text('foo% comment\r\n  bar'), 'foobar')
        self.assertEqual(self.text('foo % comment\nbar'), 'foo bar')
        self.assertEqual(self.text(r'\LaTeX document \LaTeX{} document'), 'LaTeXdocument LaTeX document')

    def test_declarations_and_grouped_skills(self):
        self.assertEqual(self.text(r'\small{\item{\textbf{Languages}: Python\\\textbf{Tools}: Git}}'),
                         'Languages: Python\nTools: Git')
        self.assertEqual(self.text(r'\begin{itemize}[leftmargin=0.15in, label={}]'), '')

    def test_unknown_visible_syntax_is_not_silently_lost(self):
        for value in (r'\unknown{important}', r'$x^2$', r'$unfinished', r'\href{only one}', r'a & b'):
            with self.subTest(value=value), self.assertRaises(LatexSyntaxError):
                self.text(value)

    def test_macro_parameter_reordering_and_override_fail(self):
        for definition in (r'\newcommand{\resumeSubheading}[4]{#3 #2 #1 #4}',
                           r'\newcommand{\resumeSubheading}[3]{#1 #2 #3}',
                           r'\renewcommand{\textbf}[1]{Changed}',
                           r'\newcommand{\resumeItem}[1]{Invented #1}'):
            source = SourceSnapshot(Path('/synthetic/main.tex'),
                                    (definition + r'\begin{document}\section{Skills}Text\end{document}').encode())
            with self.assertRaises(LatexSyntaxError):
                parse_cv(source)

    def test_source_and_snapshot_are_unchanged(self):
        source = SourceSnapshot.read(FIXTURES / 'synthetic.tex')
        original = source.raw
        self.assertEqual(parse_cv(source), parse_cv(source))
        self.assertEqual(source.path.read_bytes(), original)


if __name__ == '__main__':
    unittest.main()
