from pathlib import Path
import unittest

from scripts.cv_latex import LatexSyntaxError, scan_latex
from scripts.cv_source import SourceSnapshot


class LatexScannerTests(unittest.TestCase):
    def scan(self, text):
        source = SourceSnapshot(Path('/synthetic/main.tex'), text.encode())
        return source, scan_latex(source)

    def assert_partition(self, source, nodes, start, end):
        cursor = start
        for node in nodes:
            self.assertEqual(node.start_byte, cursor)
            self.assertGreater(node.end_byte, node.start_byte)
            self.assertEqual(node.raw(source).encode(), source.raw[node.start_byte:node.end_byte])
            if node.kind == 'group':
                self.assertEqual(node.body_start_byte, node.start_byte + 1)
                self.assertEqual(node.body_end_byte, node.end_byte - 1)
                self.assert_partition(source, node.children, node.body_start_byte, node.body_end_byte)
            cursor = node.end_byte
        self.assertEqual(cursor, end)

    def test_nested_commands_and_exact_empty_body(self):
        source, nodes = self.scan(r'\resumeItem{Café \textbf{\emph{fast}}}\resumeItem{}')
        self.assertEqual([n.kind for n in nodes], ['command', 'group', 'command', 'group'])
        self.assertEqual(nodes[0].name, 'resumeItem')
        self.assertEqual(nodes[1].children[2].name, 'textbf')
        self.assertEqual(nodes[3].children, ())
        self.assertEqual(nodes[3].body_start_byte, nodes[3].body_end_byte)
        self.assert_partition(source, nodes, 0, len(source.raw))

    def test_comments_hide_commands_braces_and_consume_newline(self):
        for newline in ('\n', '\r\n', '\r'):
            source, nodes = self.scan('a% } \\resumeItem{hidden' + newline + 'b')
            self.assertEqual([n.kind for n in nodes], ['text', 'comment', 'text'])
            self.assertTrue(nodes[1].raw(source).endswith(newline))
            self.assertEqual(nodes[2].span(source)['start'], {'line': 2, 'column': 1})
            self.assertEqual(''.join(n.raw(source) for n in nodes if n.kind != 'comment'), 'ab')
        source, nodes = self.scan('x% trailing comment')
        self.assertEqual(nodes[-1].end_byte, len(source.raw))

    def test_escaped_delimiters_and_backslash_parity(self):
        source, nodes = self.scan(r'\{\}\%\&\_\$\\% ignored }')
        self.assertEqual([n.name for n in nodes[:-1]], ['{', '}', '%', '&', '_', '$', '\\'])
        self.assertEqual(nodes[-1].kind, 'comment')
        self.assert_partition(source, nodes, 0, len(source.raw))

    def test_siblings_keep_optional_arguments_stars_and_trivia(self):
        source, nodes = self.scan('\\section*[Short] % comment\n{Long}')
        self.assertEqual(nodes[0].name, 'section')
        self.assertEqual(nodes[1].raw(source), '*[Short]')
        self.assertEqual(nodes[-1].kind, 'group')
        self.assert_partition(source, nodes, 0, len(source.raw))

    def test_math_delimiters_are_recorded_without_interpretation(self):
        source, nodes = self.scan(r'$\sim$ $$x$$ \$')
        self.assertEqual([n.name for n in nodes if n.kind == 'math_delimiter'], ['$', '$', '$$', '$$'])
        self.assertEqual(nodes[-1].kind, 'control_symbol')
        self.assert_partition(source, nodes, 0, len(source.raw))

    def test_located_errors_do_not_expose_source_text(self):
        for text, code, start in [('é}', 'unexpected_close_brace', 2),
                                  ('é{secret', 'unclosed_group', 2),
                                  ('é\\', 'incomplete_command', 2)]:
            with self.subTest(code=code), self.assertRaises(LatexSyntaxError) as caught:
                self.scan(text)
            self.assertEqual(caught.exception.code, code)
            self.assertEqual(caught.exception.span['start_byte'], start)
            self.assertEqual(caught.exception.span['start'], {'line': 1, 'column': 2})
            self.assertNotIn('secret', str(caught.exception))

    def test_nesting_limit_is_controlled(self):
        source = SourceSnapshot(Path('/synthetic/main.tex'), b'{{{x}}}')
        self.assertEqual(scan_latex(source, max_depth=3)[0].kind, 'group')
        with self.assertRaises(LatexSyntaxError) as caught:
            scan_latex(source, max_depth=2)
        self.assertEqual(caught.exception.code, 'nesting_limit')

    def test_lexical_overrides_are_rejected(self):
        for text in (r'\verb|{}|', r'\catcode', r'\makeatletter', r'\ExplSyntaxOn'):
            with self.assertRaises(LatexSyntaxError) as caught:
                self.scan(text)
            self.assertEqual(caught.exception.code, 'unsupported_lexical_command')

    def test_synthetic_document_is_lossless_and_source_unchanged(self):
        path = Path(__file__).parent / 'fixtures/parser/synthetic.tex'
        source = SourceSnapshot.read(path)
        nodes = scan_latex(source)
        self.assert_partition(source, nodes, 0, len(source.raw))
        self.assertEqual(path.read_bytes(), source.raw)
        self.assertEqual(''.join(n.raw(source) for n in nodes), source.text)

    def test_empty_input_and_control_newline(self):
        self.assertEqual(self.scan('')[1], ())
        source, nodes = self.scan('\\\r\nx')
        self.assertEqual(nodes[0].name, '\r\n')
        self.assertEqual(nodes[1].span(source)['start'], {'line': 2, 'column': 1})


if __name__ == '__main__':
    unittest.main()
