import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from scripts.cv_source import SourceEncodingError, SourceSnapshot

FIXTURES = Path(__file__).parent / "fixtures/parser"


class SourceSnapshotTests(unittest.TestCase):
    def snapshot(self, raw):
        return SourceSnapshot(Path('/synthetic/main.tex'), raw)

    def test_reads_exact_bytes_and_snapshot_survives_disk_change(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'main.tex'
            original = 'Aé\r\nB\n'.encode()
            path.write_bytes(original)
            first = SourceSnapshot.read(path)
            self.assertEqual(first.raw, original)
            self.assertEqual(first.text, 'Aé\r\nB\n')
            self.assertEqual(first.sha256, hashlib.sha256(original).hexdigest())
            self.assertEqual(first.path, path.resolve())
            self.assertEqual(path.read_bytes(), original)
            path.write_bytes(original.replace(b'\r\n', b'\n'))
            self.assertNotEqual(SourceSnapshot.read(path).sha256, first.sha256)
            self.assertEqual(first.raw, original)
            path.unlink()
            with self.assertRaises(FileNotFoundError):
                SourceSnapshot.read(path)

    def test_unicode_offsets_and_positions(self):
        source = self.snapshot('Aé🙂\tZ\r\nβ\n'.encode())
        # Explicit values independently specify the byte/code-point contract.
        expected = [(0, 1, 1), (1, 1, 2), (3, 1, 3), (7, 1, 4),
                    (8, 1, 5), (9, 1, 6), (10, 1, 7),
                    (11, 2, 1), (13, 2, 2), (14, 3, 1)]
        for character, (byte, line, column) in enumerate(expected):
            self.assertEqual(source.byte_offset(character), byte)
            self.assertEqual(source.character_offset(byte), character)
            self.assertEqual(source.position(byte), {'line': line, 'column': column})
        self.assertEqual(source.slice_text(1, 7), 'é🙂')
        self.assertEqual(source.span_from_characters(1, 3), {
            'start_byte': 1, 'end_byte': 7,
            'start': {'line': 1, 'column': 2}, 'end': {'line': 1, 'column': 4}})

    def test_newlines_empty_source_eof_and_empty_body(self):
        empty = self.snapshot(b'')
        self.assertEqual(empty.position(0), {'line': 1, 'column': 1})
        self.assertEqual(empty.slice_text(0, 0), '')
        for raw in (b'A\nB', b'A\r\nB', b'A\rB'):
            source = self.snapshot(raw)
            self.assertEqual(source.position(len(raw)), {'line': 2, 'column': 2})
        source = self.snapshot(b'\\resumeItem{}')
        self.assertEqual(source.slice_text(12, 12), '')
        self.assertEqual(source.span(12, 12)['start'], source.span(12, 12)['end'])

    def test_bom_and_combining_characters_are_preserved(self):
        source = self.snapshot('\ufeffe\u0301'.encode())
        self.assertEqual(source.text, '\ufeffe\u0301')
        self.assertEqual(source.byte_offset(1), 3)
        self.assertEqual(source.position(len(source.raw)), {'line': 1, 'column': 4})

    def test_invalid_encoding_has_safe_diagnostic(self):
        with self.assertRaises(SourceEncodingError) as caught:
            self.snapshot(b'private text\xff')
        self.assertEqual(caught.exception.code, 'invalid_utf8')
        self.assertEqual((caught.exception.start_byte, caught.exception.end_byte), (12, 13))
        self.assertNotIn('private text', str(caught.exception))

    def test_rejects_invalid_ranges_and_mid_character_offsets(self):
        source = self.snapshot('é'.encode())
        for invalid in (-1, 3):
            with self.assertRaises(ValueError):
                source.position(invalid)
        with self.assertRaises(ValueError):
            source.position(1)
        with self.assertRaises(ValueError):
            source.span(2, 0)
        with self.assertRaises(ValueError):
            source.byte_offset(2)
        for invalid in (True, 0.0, '0'):
            with self.assertRaises(TypeError):
                source.position(invalid)
        with self.assertRaises(TypeError):
            self.snapshot(bytearray(b'abc'))

    def test_locations_match_all_authored_contract_spans(self):
        source = SourceSnapshot.read(FIXTURES / 'synthetic.tex')
        expected = json.loads((FIXTURES / 'expected.json').read_text())
        self.assertEqual(source.sha256, expected['source_sha256'])
        checked = 0
        def walk(value):
            nonlocal checked
            if isinstance(value, list):
                for child in value:
                    walk(child)
            elif isinstance(value, dict):
                for key, child in value.items():
                    if key in ('span', 'body_span'):
                        self.assertEqual(source.span(child['start_byte'], child['end_byte']), child)
                        checked += 1
                    else:
                        walk(child)
        walk(expected)
        self.assertGreater(checked, 20)


if __name__ == '__main__':
    unittest.main()
