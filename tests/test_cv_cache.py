from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
SPEC = importlib.util.spec_from_file_location("cv_cache", ROOT / "scripts" / "cv_cache.py")
assert SPEC and SPEC.loader
CACHE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = CACHE
SPEC.loader.exec_module(CACHE)

CV_SOURCE = r"""\newcommand{\resumeItem}[1]{\item #1}
\begin{document}
\begin{center}
\textbf{\Huge Example Person} \\
\href{mailto:hidden@example.com}{person@example.com}
\end{center}
\section{Education}
\resumeSubHeadingListStart
\resumeSubheading{Example University}{2020 -- 2024}{BSc Computer Science}{London}
\resumeSubHeadingListEnd
\section{Experience}
\resumeSubheading{Engineer}{2024 -- Present}{Example Company}{Remote}
\resumeItemListStart
\resumeItem{Built \textbf{an API} using Go.}
\resumeItem{Cut latency by 30\%.}
\resumeItemListEnd
\section{Projects}
\resumeProjectHeading{\textbf{Example Project} $|$ \emph{Python}}{2024}
\resumeItemListStart
\resumeItem{Processed records with Python.}
\resumeItemListEnd
\section{Technical Skills}
\begin{itemize}[leftmargin=0.15in, label={}]
\small{\item{\textbf{Languages}{: Go, Python} \\ \textbf{Tools}{: Git}}}
\end{itemize}
\end{document}
"""


class CvCacheTests(unittest.TestCase):
    def setUp(self) -> None:
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        self.cv = self.root / "main.tex"
        self.cv.write_text(CV_SOURCE, encoding="utf-8")
        self.cache_dir = self.root / "cache"

    def ensure(self):
        return CACHE.ensure_parsed(self.cv, cache_dir=self.cache_dir)

    def test_unchanged_source_reuses_cache_without_parsing_or_writing(self) -> None:
        before, status, path = self.ensure()
        self.assertEqual("rebuilt", status)
        before_stat = path.stat()
        with patch.object(CACHE, "parse_snapshot", side_effect=AssertionError("should reuse")):
            after, status, _ = self.ensure()
        self.assertEqual("reused", status)
        self.assertEqual(before, after)
        self.assertEqual(before_stat.st_mtime_ns, path.stat().st_mtime_ns)
        self.assertEqual(CV_SOURCE, self.cv.read_text(encoding="utf-8"))

    def test_content_changes_invalidate_even_with_same_size_and_mtime(self) -> None:
        before, _, _ = self.ensure()
        old_stat = self.cv.stat()
        self.cv.write_text(CV_SOURCE.replace("30\\%", "40\\%"), encoding="utf-8")
        os.utime(self.cv, ns=(old_stat.st_atime_ns, old_stat.st_mtime_ns))
        after, status, _ = self.ensure()
        self.assertEqual("rebuilt", status)
        self.assertNotEqual(before["source"]["sha256"], after["source"]["sha256"])
        self.assertIn("40%", after["parsed"]["content"]["targets"][0]["bullets"][1])

    def test_parser_changes_invalidate_unchanged_cv(self) -> None:
        before, _, _ = self.ensure()
        with patch.object(CACHE, "parser_fingerprint", return_value="new-parser"):
            after, status, _ = self.ensure()
        self.assertEqual("rebuilt", status)
        self.assertEqual(before["source"], after["source"])
        self.assertEqual("new-parser", after["parser_sha256"])

    def test_parser_fingerprint_covers_each_helper_and_schema(self) -> None:
        helpers = [self.root / f"parser-{index}.py" for index in range(3)]
        for helper in helpers:
            helper.write_text("original", encoding="utf-8")
        with patch.object(CACHE, "PARSER_FILES", tuple(helpers)):
            original = CACHE.parser_fingerprint()
            for helper in helpers:
                helper.write_text("changed", encoding="utf-8")
                self.assertNotEqual(original, CACHE.parser_fingerprint())
                helper.write_text("original", encoding="utf-8")
            with patch.object(CACHE, "SCHEMA_VERSION", CACHE.SCHEMA_VERSION + 1):
                self.assertNotEqual(original, CACHE.parser_fingerprint())

    def test_corrupt_or_incomplete_cache_rebuilds(self) -> None:
        document, _, path = self.ensure()
        corruptions = ["{not json", "[]", json.dumps({"schema_version": 1})]
        document["parsed"]["content"]["targets"] = []
        corruptions.append(json.dumps(document))
        for corruption in corruptions:
            with self.subTest(corruption=corruption):
                path.write_text(corruption, encoding="utf-8")
                rebuilt, status, _ = self.ensure()
                self.assertEqual("rebuilt", status)
                self.assertEqual("Example Company", rebuilt["parsed"]["content"]["targets"][0]["name"])

    def test_parse_failure_removes_stale_cache(self) -> None:
        _, _, path = self.ensure()
        self.cv.write_text(CV_SOURCE.replace("using Go", r"using \textbf{Go"), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "Unclosed brace"):
            self.ensure()
        self.assertFalse(path.exists())

    def test_missing_source_removes_stale_cache(self) -> None:
        _, _, path = self.ensure()
        self.cv.unlink()
        with self.assertRaises(FileNotFoundError):
            self.ensure()
        self.assertFalse(path.exists())

    def test_source_change_during_parse_is_rejected(self) -> None:
        parse = CACHE.parse_snapshot

        def change_source(source):
            result = parse(source)
            self.cv.write_text(CV_SOURCE.replace("using Go", "using Java"), encoding="utf-8")
            return result

        with patch.object(CACHE, "parse_snapshot", side_effect=change_source):
            with self.assertRaisesRegex(ValueError, "changed during parsing"):
                self.ensure()
        self.assertFalse(CACHE.cache_path_for(self.cv, self.cache_dir).exists())

    def test_parser_change_during_parse_is_rejected(self) -> None:
        with patch.object(CACHE, "parser_fingerprint", side_effect=["before", "after"]):
            with self.assertRaisesRegex(ValueError, "changed during parsing"):
                self.ensure()
        self.assertFalse(CACHE.cache_path_for(self.cv, self.cache_dir).exists())

    def test_cache_write_failure_does_not_leave_partial_or_stale_cache(self) -> None:
        _, _, path = self.ensure()
        self.cv.write_text(CV_SOURCE.replace("using Go", "using Java"), encoding="utf-8")
        with patch.object(CACHE.os, "replace", side_effect=OSError("failed write")):
            with self.assertRaisesRegex(OSError, "failed write"):
                self.ensure()
        self.assertFalse(path.exists())
        self.assertEqual([], list(self.cache_dir.glob("*.tmp")))


    def test_bolding_invalidates_cache_but_preserves_semantic_content(self) -> None:
        before, _, _ = self.ensure()
        self.cv.write_text(CV_SOURCE.replace(r"\textbf{an API}", "an API"), encoding="utf-8")
        after, status, _ = self.ensure()
        self.assertEqual("rebuilt", status)
        self.assertEqual(before["parsed"]["content"], after["parsed"]["content"])
        self.assertNotEqual(before["parsed"]["edit"], after["parsed"]["edit"])

    def test_same_basename_in_different_folders_has_separate_cache(self) -> None:
        another = self.root / "other" / "main.tex"
        self.assertNotEqual(CACHE.cache_path_for(self.cv, self.cache_dir), CACHE.cache_path_for(another, self.cache_dir))

    def test_crlf_offsets_still_refer_to_original_source(self) -> None:
        source = CV_SOURCE.replace("\n", "\r\n")
        self.cv.write_bytes(source.encode("utf-8"))
        document, _, _ = self.ensure()
        bullet = document["parsed"]["edit"]["targets"][0]["bullets"][0]
        self.assertEqual(bullet["latex"], source[bullet["content_start"]:bullet["content_end"]])
        self.assertEqual(source.encode("utf-8"), self.cv.read_bytes())



    def test_cli_content_view_reuses_snapshot_and_excludes_edit_metadata(self) -> None:
        command = [sys.executable, "-B", str(ROOT / "scripts" / "cv_cache.py"), str(self.cv),
                   "--cache-dir", str(self.cache_dir), "--view", "content"]
        first = subprocess.run(command, capture_output=True, text=True, check=True)
        second = subprocess.run(command, capture_output=True, text=True, check=True)
        self.assertEqual("rebuilt", json.loads(first.stdout)["status"])
        result = json.loads(second.stdout)
        self.assertEqual("reused", result["status"])
        self.assertIn("content", result)
        self.assertNotIn("edit", result)
        self.assertNotIn("content_start", second.stdout)


if __name__ == "__main__":
    unittest.main()
