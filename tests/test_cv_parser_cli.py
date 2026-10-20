import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'scripts/cv_parser.py'
FIXTURES = ROOT / 'tests/fixtures/parser'


class ParserCliTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.workspace = self.root / 'workspace'
        self.workspace.mkdir()
        self.source = self.workspace / 'main.tex'
        self.original = (FIXTURES / 'synthetic.tex').read_bytes()
        self.source.write_bytes(self.original)

    def run_cli(self, command, *options):
        return subprocess.run([sys.executable, str(SCRIPT), command, str(self.source), *options],
                              cwd=self.root, capture_output=True, text=True, timeout=10)

    def test_full_workflow_text_json_entries_and_cache_repair(self):
        text = self.run_cli('inspect')
        self.assertEqual(text.returncode, 0, text.stderr)
        self.assertEqual(text.stdout, (FIXTURES / 'expected.txt').read_text())
        cached = self.workspace / '.cache/cv/main.txt'
        cached.write_text('stale')
        inspected = self.run_cli('inspect', '--json')
        self.assertEqual(inspected.returncode, 0, inspected.stderr)
        expected = json.loads((FIXTURES / 'expected.json').read_text())
        expected['source_path'] = str(self.source.resolve())
        self.assertEqual(json.loads(inspected.stdout), expected)
        self.assertEqual(cached.read_text(), text.stdout)
        listed = self.run_cli('list', '--json')
        self.assertEqual(listed.returncode, 0, listed.stderr)
        entries = json.loads(listed.stdout)['entries']
        self.assertEqual([e['id'] for e in entries], ['s1.e1', 's2.e1', 's3.e1'])
        self.assertEqual(entries[1]['empty_bullet_count'], 1)
        self.assertEqual(self.source.read_bytes(), self.original)

    def test_failed_parse_has_no_partial_stdout_or_cache(self):
        self.source.write_text(r'\begin{document}\unknown{private words}\end{document}')
        result = self.run_cli('inspect')
        self.assertEqual(result.returncode, 1)
        self.assertEqual(result.stdout, '')
        self.assertEqual(json.loads(result.stderr)['code'], 'unsupported_command')
        self.assertNotIn('private words', result.stderr)
        self.assertFalse((self.workspace / '.cache').exists())

    def test_no_cache_is_read_only(self):
        result = self.run_cli('list', '--no-cache')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('s2.e1', result.stdout)
        self.assertFalse((self.workspace / '.cache').exists())
        self.assertEqual(self.source.read_bytes(), self.original)

    def test_missing_source_and_duplicate_entries(self):
        self.source.unlink()
        self.assertEqual(self.run_cli('inspect').returncode, 1)
        entry = r'\resumeSubheading{Engineer}{2025}{Example}{Remote}\resumeItem{Result}'
        self.source.write_text(r'\begin{document}\section{Experience}' + entry + entry + r'\end{document}')
        result = self.run_cli('list', '--json')
        self.assertEqual(result.returncode, 0, result.stderr)
        entries = json.loads(result.stdout)['entries']
        self.assertEqual([e['id'] for e in entries], ['s1.e1', 's1.e2'])
        self.assertEqual(entries[0]['heading'], entries[1]['heading'])

    def test_grouped_skills_and_list_options_in_complete_document(self):
        self.source.write_text(r'''\begin{document}
\section{Technical Skills}
\begin{itemize}[leftmargin=0.15in, label={}]
\small{\item{\textbf{Languages}: Python, SQL\\
\textbf{Tools}: Git}}
\end{itemize}
\end{document}''')
        result = self.run_cli('inspect')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, 'TECHNICAL SKILLS\n\nLanguages: Python, SQL\nTools: Git\n')


if __name__ == '__main__':
    unittest.main()
