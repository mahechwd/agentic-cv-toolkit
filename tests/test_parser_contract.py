"""Verify authored fixtures; this does not implement or exercise a parser."""
import hashlib
import json
from pathlib import Path
import unittest

FIXTURES = Path(__file__).parent / "fixtures" / "parser"


class ParserContractTests(unittest.TestCase):
    def setUp(self):
        self.raw = (FIXTURES / "synthetic.tex").read_bytes()
        self.record = json.loads((FIXTURES / "expected.json").read_text())

    def test_envelope_and_readable_view(self):
        self.assertEqual(self.record["source_sha256"], hashlib.sha256(self.raw).hexdigest())
        self.assertEqual(self.record["schema_version"], 1)
        self.assertEqual(self.record["parser_version"], "1")
        self.assertEqual(self.record["diagnostics"], [])
        text = (FIXTURES / "expected.txt").read_text()
        self.assertEqual(self.record["readable_text"], text)
        self.assertNotIn("Commented content", text)
        self.assertIn("25% using bounded retries.", text)
        self.assertIn("\n•\n", text)
        self.assertEqual([s["title"]["text"] for s in self.record["sections"]],
                         ["Education", "Experience", "Projects", "Technical Skills"])

    def check_span(self, span):
        start, end = span["start_byte"], span["end_byte"]
        self.assertGreaterEqual(start, 0)
        self.assertGreaterEqual(end, start)
        self.assertLessEqual(end, len(self.raw))
        for offset, position in ((start, span["start"]), (end, span["end"])):
            prefix = self.raw[:offset].decode("utf-8")
            self.assertEqual(position, {"line": prefix.count("\n") + 1,
                                       "column": len(prefix.rsplit("\n", 1)[-1]) + 1})
        return self.raw[start:end].decode("utf-8")

    def test_all_source_locations_and_node_relationships(self):
        ids = set()
        bullets = []
        def walk(value, parent_span=None):
            if isinstance(value, list):
                for item in value:
                    walk(item, parent_span)
            elif isinstance(value, dict):
                current = parent_span
                if "id" in value:
                    self.assertNotIn(value["id"], ids)
                    ids.add(value["id"])
                    current = value["span"]
                    extracted = self.check_span(current)
                    if "raw_latex" in value:
                        self.assertEqual(extracted, value["raw_latex"])
                    if parent_span:
                        self.assertGreaterEqual(current["start_byte"], parent_span["start_byte"])
                        self.assertLessEqual(current["end_byte"], parent_span["end_byte"])
                    if value["kind"] == "bullet":
                        bullets.append(value)
                        self.assertEqual(self.check_span(value["body_span"]), value["body_latex"])
                        self.assertEqual(value["raw_latex"], "\\resumeItem{" + value["body_latex"] + "}")
                        self.assertEqual(value["body_span"]["start_byte"], current["start_byte"] + len(b"\\resumeItem{"))
                        self.assertEqual(value["body_span"]["end_byte"], current["end_byte"] - 1)
                for key, child in value.items():
                    if key not in {"span", "body_span"}:
                        walk(child, current)
        walk(self.record)
        self.assertEqual(len(bullets), 3)
        empty = [b for b in bullets if not b["body_latex"]]
        self.assertEqual(len(empty), 1)
        self.assertEqual(empty[0]["text"], "")
        self.assertEqual(empty[0]["body_span"]["start_byte"], empty[0]["body_span"]["end_byte"])


if __name__ == "__main__":
    unittest.main()
