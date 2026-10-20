import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from scripts import cv_text
from scripts.cv_cache import load_cv, SourceChangedError, _canonical
from scripts.cv_latex import LatexSyntaxError

FIXTURE = Path(__file__).parent / 'fixtures/parser/synthetic.tex'


class CacheTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.workspace = Path(self.temp.name) / 'workspace'
        self.workspace.mkdir()
        self.source = self.workspace / 'main.tex'
        self.source.write_bytes(FIXTURE.read_bytes())
        self.json = self.workspace / '.cache/cv/main.json'
        self.text = self.workspace / '.cache/cv/main.txt'

    def test_reuses_valid_cache_without_parsing_and_repairs_text(self):
        first = load_cv(self.source)
        self.assertEqual(first.status, 'rebuilt')
        self.text.write_text('stale')
        with patch.object(cv_text, 'parse_cv', side_effect=AssertionError('must not parse')):
            second = load_cv(self.source)
        self.assertEqual(second.status, 'hit')
        self.assertEqual(first.record, second.record)
        self.assertEqual(self.text.read_text(), first.record['readable_text'])

    def test_source_version_and_schema_changes_trigger_reparse(self):
        load_cv(self.source)
        original = cv_text.parse_cv
        with patch.object(cv_text, 'parse_cv', wraps=original) as parse:
            self.source.write_bytes(self.source.read_bytes().replace(b'2025', b'2024'))
            self.assertEqual(load_cv(self.source).status, 'rebuilt')
            with patch.object(cv_text, 'PARSER_VERSION', '2'):
                self.assertEqual(load_cv(self.source).status, 'rebuilt')
            with patch.object(cv_text, 'SCHEMA_VERSION', 2):
                self.assertEqual(load_cv(self.source).status, 'rebuilt')
            self.assertEqual(parse.call_count, 3)

    def test_corrupt_cache_and_invalid_locations_regenerate(self):
        load_cv(self.source)
        self.json.write_text('{bad json')
        self.assertEqual(load_cv(self.source).status, 'rebuilt')
        record = json.loads(self.json.read_text())
        record.pop('cache_sha256')
        record['sections'][0]['span']['start_byte'] = -1
        record['cache_sha256'] = hashlib.sha256(_canonical(record)).hexdigest()
        self.json.write_text(json.dumps(record))
        self.assertEqual(load_cv(self.source).status, 'rebuilt')

    def test_deleted_or_invalid_source_never_returns_stale_cache(self):
        load_cv(self.source)
        self.source.write_text(r'\begin{document}\unknown{hidden}\end{document}')
        with self.assertRaises(LatexSyntaxError):
            load_cv(self.source)
        self.source.unlink()
        with self.assertRaises(FileNotFoundError):
            load_cv(self.source)

    def test_interrupted_text_write_recovers_on_next_request(self):
        from scripts.cv_cache import _atomic_write
        def interrupted(path, data):
            if path.suffix == '.txt':
                raise OSError('interrupted')
            return _atomic_write(path, data)
        with patch('scripts.cv_cache._atomic_write', side_effect=interrupted):
            result = load_cv(self.source)
        self.assertTrue(result.warnings)
        self.assertTrue(self.json.exists())
        recovered = load_cv(self.source)
        self.assertEqual(recovered.status, 'hit')
        self.assertEqual(self.text.read_text(), recovered.record['readable_text'])

    def test_atomic_replace_failure_does_not_leave_temporary_files(self):
        with patch('scripts.cv_cache.os.replace', side_effect=OSError('failure')):
            result = load_cv(self.source)
        self.assertTrue(result.warnings)
        self.assertEqual(list(self.json.parent.iterdir()), [])

    def test_source_change_during_parse_is_rejected(self):
        original = cv_text.parse_cv
        def concurrent(source):
            record = original(source)
            self.source.write_bytes(self.source.read_bytes() + b'\n')
            return record
        with patch.object(cv_text, 'parse_cv', side_effect=concurrent), self.assertRaises(SourceChangedError):
            load_cv(self.source)
        self.assertFalse(self.json.exists())

    def test_main_and_tailored_have_independent_cache_records(self):
        first = load_cv(self.source)
        tailored = self.workspace / 'tailored.tex'
        tailored.write_bytes(self.source.read_bytes().replace(b'25', b'30'))
        second = load_cv(tailored)
        self.assertNotEqual(first.record['source_sha256'], second.record['source_sha256'])
        self.assertTrue((self.json.parent / 'tailored.json').exists())
        self.assertEqual(load_cv(self.source).status, 'hit')

    def test_cache_path_restrictions_and_no_cache_mode(self):
        other = Path(self.temp.name) / 'example.tex'
        other.write_bytes(FIXTURE.read_bytes())
        with self.assertRaises(ValueError):
            load_cv(other)
        self.assertEqual(load_cv(other, use_cache=False).status, 'disabled')
        (self.workspace / '.cache').symlink_to(Path(self.temp.name), target_is_directory=True)
        with self.assertRaises(ValueError):
            load_cv(self.source)


if __name__ == '__main__':
    unittest.main()
