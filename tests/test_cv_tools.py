from __future__ import annotations

import importlib.util
import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("cv_tex", ROOT / "scripts" / "cv_tex.py")
assert SPEC and SPEC.loader
CV_TEX = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = CV_TEX
SPEC.loader.exec_module(CV_TEX)

PREPARE_SPEC = importlib.util.spec_from_file_location(
    "prepare_application",
    ROOT / "scripts" / "prepare_application.py",
)
assert PREPARE_SPEC and PREPARE_SPEC.loader
PREPARE = importlib.util.module_from_spec(PREPARE_SPEC)
sys.modules[PREPARE_SPEC.name] = PREPARE
PREPARE_SPEC.loader.exec_module(PREPARE)

SETUP_SPEC = importlib.util.spec_from_file_location(
    "setup_workspace",
    ROOT / "scripts" / "setup_workspace.py",
)
assert SETUP_SPEC and SETUP_SPEC.loader
SETUP = importlib.util.module_from_spec(SETUP_SPEC)
sys.modules[SETUP_SPEC.name] = SETUP
SETUP_SPEC.loader.exec_module(SETUP)

CV_DRAFTS_SPEC = importlib.util.spec_from_file_location(
    "cv_drafts",
    ROOT / "scripts" / "cv_drafts.py",
)
assert CV_DRAFTS_SPEC and CV_DRAFTS_SPEC.loader
CV_DRAFTS = importlib.util.module_from_spec(CV_DRAFTS_SPEC)
sys.modules[CV_DRAFTS_SPEC.name] = CV_DRAFTS
CV_DRAFTS_SPEC.loader.exec_module(CV_DRAFTS)


CV_SOURCE = r"""
\newcommand{\resumeItem}[1]{#1}
\begin{document}
\section{Experience}
% \resumeSubheading{Ignored Role}{Now}{Ignored Company}{Remote}
% \resumeItemListStart
% \resumeItem{Ignored bullet}
% \resumeItemListEnd
\resumeSubheading
  {Software Engineer}{2025 -- 2026}
  {Example Company}{London}
  \resumeItemListStart
    \resumeItem{Built a reliable API using Go.}
    \resumeItem{}
  \resumeItemListEnd
\section{Projects}
\resumeProjectHeading
  {\textbf{Example Project} $|$ \emph{Python, PostgreSQL}}{}
  \resumeItemListStart
    \resumeItem{Processed 10,000 records with Python.}
  \resumeItemListEnd
\end{document}
"""


class CvTexTests(unittest.TestCase):
    def test_extracts_nested_bold_text_and_ignores_comments(self) -> None:
        source = r"""
\newcommand{\resumeItem}[1]{#1}
\begin{document}
% \resumeItem{ignored}
\resumeItem{Improved retrieval by \textbf{30\%} using \textbf{Elasticsearch}.}
\resumeItem{Handled \$5M and R\&D data with $\sim$3s latency.}
\end{document}
"""
        with tempfile.TemporaryDirectory() as temporary_directory:
            path = Path(temporary_directory) / "main.tex"
            path.write_text(source, encoding="utf-8")
            bullets = CV_TEX.extract_bullets(path)

        self.assertEqual(2, len(bullets))
        self.assertEqual(
            "Improved retrieval by 30% using Elasticsearch.",
            bullets[0].rendered,
        )
        self.assertEqual(
            "Handled $5M and R&D data with ~3s latency.",
            bullets[1].rendered,
        )

    def test_reports_unclosed_resume_item(self) -> None:
        source = "\\begin{document}\n\\resumeItem{broken\n"
        with tempfile.TemporaryDirectory() as temporary_directory:
            path = Path(temporary_directory) / "main.tex"
            path.write_text(source, encoding="utf-8")
            with self.assertRaises(ValueError):
                CV_TEX.extract_bullets(path)

    def test_masks_comments_without_changing_offsets(self) -> None:
        source = "before % comment with {braces}\r\nafter \\% visible\r\n"
        masked = CV_TEX.mask_comments(source)
        self.assertEqual(len(source), len(masked))
        self.assertEqual(source.count("\n"), masked.count("\n"))
        self.assertIn(r"\% visible", masked)
        self.assertNotIn("comment", masked)


class CvDraftTests(unittest.TestCase):
    def _workspace(self, root: Path) -> tuple[Path, Path]:
        cv = root / "main.tex"
        draft = root / "drafts" / "build" / "example-company.json"
        cv.write_text(CV_SOURCE, encoding="utf-8")
        return cv, draft

    def test_lists_exact_experience_and_project_targets(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            cv, _ = self._workspace(Path(temporary_directory))
            targets = CV_DRAFTS.scan_targets(cv)

        self.assertEqual(
            [("experience", "Example Company", 2), ("project", "Example Project", 1)],
            [(target.kind, target.name, len(target.bullets)) for target in targets],
        )
        self.assertEqual("Software Engineer", targets[0].context)
        self.assertNotIn("Ignored Company", [target.name for target in targets])

    def test_initialises_existing_and_empty_bullet_slots(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            cv, draft_path = self._workspace(Path(temporary_directory))
            draft = CV_DRAFTS.initialise_draft(
                cv,
                "experience",
                "Example Company",
                draft_path,
            )

        self.assertEqual("draft", draft["status"])
        self.assertEqual(2, draft["expected_bullet_count"])
        self.assertEqual("Built a reliable API using Go.", draft["existing_bullets"][0]["rendered"])
        self.assertEqual("", draft["existing_bullets"][1]["rendered"])
        self.assertEqual(
            ["Built a reliable API using Go.", ""],
            draft["proposed_bullets"],
        )

    def test_requires_approval_before_apply(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            cv, draft_path = self._workspace(Path(temporary_directory))
            CV_DRAFTS.initialise_draft(cv, "experience", "Example Company", draft_path)
            with self.assertRaises(PermissionError):
                CV_DRAFTS.apply_draft(cv, draft_path)

    def test_preview_changes_copy_without_changing_source(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            cv, draft_path = self._workspace(root)
            original = cv.read_text(encoding="utf-8")
            draft = CV_DRAFTS.initialise_draft(
                cv,
                "project",
                "Example Project",
                draft_path,
            )
            draft["proposed_bullets"] = ["Improved the project bullet."]
            draft_path.write_text(json.dumps(draft), encoding="utf-8")
            preview = root / "drafts" / "previews" / "project.tex"

            CV_DRAFTS.preview_draft(cv, draft_path, preview)

            self.assertEqual(original, cv.read_text(encoding="utf-8"))
            self.assertIn("Improved the project bullet.", preview.read_text(encoding="utf-8"))
            self.assertNotIn("Improved the project bullet.", original)

    def test_applies_only_resume_item_contents_and_creates_backup(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            cv, draft_path = self._workspace(Path(temporary_directory))
            original = cv.read_text(encoding="utf-8")
            draft = CV_DRAFTS.initialise_draft(
                cv,
                "experience",
                "Example Company",
                draft_path,
            )
            draft["status"] = "approved"
            draft["proposed_bullets"] = [
                r"Reduced API latency by 30\% using Go caching.",
                r"Added contract tests for 12 endpoints.",
            ]
            draft_path.write_text(json.dumps(draft), encoding="utf-8")

            backup = CV_DRAFTS.apply_draft(cv, draft_path)
            updated = cv.read_text(encoding="utf-8")
            applied = json.loads(draft_path.read_text(encoding="utf-8"))

            expected = original.replace(
                "Built a reliable API using Go.",
                r"Reduced API latency by 30\% using Go caching.",
            ).replace(
                r"\resumeItem{}",
                r"\resumeItem{Added contract tests for 12 endpoints.}",
                1,
            )
            self.assertEqual(expected, updated)
            self.assertEqual(original, backup.read_text(encoding="utf-8"))
            self.assertEqual("applied", applied["status"])
            self.assertEqual(3, len(CV_TEX.extract_bullets(cv)))
            self.assertIn("Processed 10,000 records with Python.", updated)

    def test_rejects_stale_target_and_structural_proposals(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            cv, draft_path = self._workspace(Path(temporary_directory))
            draft = CV_DRAFTS.initialise_draft(
                cv,
                "experience",
                "Example Company",
                draft_path,
            )
            draft["status"] = "approved"
            draft["proposed_bullets"] = ["Changed", "Added"]
            draft_path.write_text(json.dumps(draft), encoding="utf-8")
            cv.write_text(CV_SOURCE.replace("using Go", "using Rust"), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "stale"):
                CV_DRAFTS.apply_draft(cv, draft_path)

            cv.write_text(CV_SOURCE, encoding="utf-8")
            draft = CV_DRAFTS.initialise_draft(
                cv,
                "project",
                "Example Project",
                draft_path.with_name("example-project.json"),
            )
            draft["status"] = "approved"
            draft["proposed_bullets"] = [r"\resumeItem{Nested}"]
            structural_path = draft_path.with_name("example-project.json")
            structural_path.write_text(json.dumps(draft), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "structural"):
                CV_DRAFTS.apply_draft(cv, structural_path)

    def test_rejects_changed_bullet_count_contract(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            cv, draft_path = self._workspace(Path(temporary_directory))
            draft = CV_DRAFTS.initialise_draft(
                cv,
                "experience",
                "Example Company",
                draft_path,
            )
            draft["status"] = "approved"
            draft["expected_bullet_count"] = 1
            draft["proposed_bullets"] = ["Changed"]
            draft_path.write_text(json.dumps(draft), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "bullet count"):
                CV_DRAFTS.apply_draft(cv, draft_path)

    def test_target_length_check_passes_within_both_limits(self) -> None:
        source = CV_SOURCE.replace(
            r"\resumeItem{}",
            r"\resumeItem{Added contract tests for 12 API endpoints.}",
            1,
        )
        with tempfile.TemporaryDirectory() as temporary_directory:
            cv = Path(temporary_directory) / "main.tex"
            cv.write_text(source, encoding="utf-8")
            check = CV_DRAFTS.check_target_lengths(
                cv,
                "experience",
                "Example Company",
            )

        self.assertTrue(check.passed)
        self.assertEqual((30, 42), check.bullet_characters)
        self.assertEqual(36, check.average_characters)
        self.assertEqual(180, check.max_average)

    def test_target_length_check_rejects_bullet_over_hard_maximum(self) -> None:
        long_bullet = "A" * 221
        source = CV_SOURCE.replace(
            "Built a reliable API using Go.",
            long_bullet,
        ).replace(r"\resumeItem{}", r"\resumeItem{Short supported result.}", 1)
        with tempfile.TemporaryDirectory() as temporary_directory:
            cv = Path(temporary_directory) / "main.tex"
            cv.write_text(source, encoding="utf-8")
            check = CV_DRAFTS.check_target_lengths(
                cv,
                "experience",
                "Example Company",
            )

        self.assertFalse(check.passed)
        self.assertIn("bullet 1 is 221 characters; maximum is 220", check.violations)

    def test_target_length_check_rejects_average_over_limit(self) -> None:
        source = CV_SOURCE.replace(
            "Built a reliable API using Go.",
            "A" * 181,
        ).replace(r"\resumeItem{}", rf"\resumeItem{{{'B' * 181}}}", 1)
        with tempfile.TemporaryDirectory() as temporary_directory:
            cv = Path(temporary_directory) / "main.tex"
            cv.write_text(source, encoding="utf-8")
            check = CV_DRAFTS.check_target_lengths(
                cv,
                "experience",
                "Example Company",
            )

        self.assertFalse(check.passed)
        self.assertEqual((181, 181), check.bullet_characters)
        self.assertIn(
            "block average is 181.0 characters; maximum is 180",
            check.violations,
        )

    def test_target_length_check_ignores_other_cv_blocks(self) -> None:
        source = CV_SOURCE.replace(
            r"\resumeItem{}",
            r"\resumeItem{Added contract tests for 12 API endpoints.}",
            1,
        ).replace("Processed 10,000 records with Python.", "P" * 300)
        with tempfile.TemporaryDirectory() as temporary_directory:
            cv = Path(temporary_directory) / "main.tex"
            cv.write_text(source, encoding="utf-8")
            check = CV_DRAFTS.check_target_lengths(
                cv,
                "experience",
                "Example Company",
            )

        self.assertTrue(check.passed)

    def test_target_length_check_command_exits_unsuccessfully_on_failure(self) -> None:
        source = CV_SOURCE.replace(
            "Built a reliable API using Go.",
            "A" * 221,
        ).replace(r"\resumeItem{}", r"\resumeItem{Short supported result.}", 1)
        with tempfile.TemporaryDirectory() as temporary_directory:
            cv = Path(temporary_directory) / "main.tex"
            cv.write_text(source, encoding="utf-8")
            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "cv_drafts.py"),
                    "check",
                    "--cv",
                    str(cv),
                    "--kind",
                    "experience",
                    "--target",
                    "Example Company",
                ],
                check=False,
                capture_output=True,
                text=True,
            )

        self.assertEqual(4, result.returncode)
        self.assertIn("result: FAIL", result.stdout)


class PrepareApplicationTests(unittest.TestCase):
    def test_creates_immutable_source_and_refuses_overwrite(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            workspace = root / "workspace"
            workspace.mkdir()
            (workspace / "main.tex").write_text("canonical", encoding="utf-8")
            (workspace / "job-description.txt").write_text("vacancy", encoding="utf-8")

            destination = PREPARE.prepare_application(root, "example-engineer")

            self.assertEqual("canonical", (destination / "main.tex").read_text())
            self.assertEqual("canonical", (destination / "main.source.tex").read_text())
            self.assertEqual("vacancy", (destination / "job-description.txt").read_text())
            with self.assertRaises(FileExistsError):
                PREPARE.prepare_application(root, "example-engineer")

    def test_rejects_empty_job_description(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            workspace = root / "workspace"
            workspace.mkdir()
            (workspace / "main.tex").write_text("canonical", encoding="utf-8")
            (workspace / "job-description.txt").write_text("", encoding="utf-8")
            with self.assertRaises(ValueError):
                PREPARE.prepare_application(root, "example-engineer")


class SetupWorkspaceTests(unittest.TestCase):
    @staticmethod
    def create_templates(root: Path) -> None:
        templates = root / "templates"
        templates.mkdir()
        (templates / "main.tex").write_text("public cv template", encoding="utf-8")
        (templates / "job-description.txt").write_text(
            "public job template",
            encoding="utf-8",
        )
        evidence_template = templates / "context" / "experience" / "example-company"
        evidence_template.mkdir(parents=True)
        (evidence_template / "evidence.md").write_text(
            "public evidence template",
            encoding="utf-8",
        )

    def test_creates_private_inputs_and_never_overwrites_them(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            self.create_templates(root)

            first = SETUP.setup_workspace(root)
            workspace = root / "workspace"
            (workspace / "main.tex").write_text("private cv", encoding="utf-8")
            (workspace / "job-description.txt").write_text("private job", encoding="utf-8")
            private_evidence = (
                workspace / "context" / "experience" / "example-company" / "evidence.md"
            )
            private_evidence.write_text("private evidence", encoding="utf-8")
            second = SETUP.setup_workspace(root)

            self.assertEqual("created from template", first["workspace/main.tex"])
            self.assertEqual(
                "created from template",
                first["workspace/job-description.txt"],
            )
            self.assertEqual("created from template", first["workspace/context/"])
            self.assertEqual("kept existing", second["workspace/main.tex"])
            self.assertEqual(
                "kept existing",
                second["workspace/job-description.txt"],
            )
            self.assertEqual("kept existing", second["workspace/context/"])
            self.assertEqual(
                "private cv",
                (workspace / "main.tex").read_text(encoding="utf-8"),
            )
            self.assertEqual(
                "private job",
                (workspace / "job-description.txt").read_text(encoding="utf-8"),
            )
            self.assertEqual("private evidence", private_evidence.read_text(encoding="utf-8"))

    def test_migrates_legacy_private_inputs_without_overwriting(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            self.create_templates(root)
            (root / "main.tex").write_text("legacy cv", encoding="utf-8")
            (root / "job-description.txt").write_text("legacy job", encoding="utf-8")
            legacy_context = root / "cv-context"
            legacy_context.mkdir()
            (legacy_context / "notes.txt").write_text("legacy evidence", encoding="utf-8")

            results = SETUP.setup_workspace(root)

            self.assertEqual("migrated legacy input", results["workspace/main.tex"])
            self.assertEqual(
                "migrated legacy input",
                results["workspace/job-description.txt"],
            )
            self.assertEqual("migrated legacy input", results["workspace/context/"])
            self.assertEqual(
                "legacy cv",
                (root / "workspace" / "main.tex").read_text(encoding="utf-8"),
            )
            self.assertFalse((root / "main.tex").exists())

    def test_fails_when_a_tracked_template_is_missing(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            with self.assertRaises(FileNotFoundError):
                SETUP.setup_workspace(Path(temporary_directory))


class SkillNamingTests(unittest.TestCase):
    def test_all_repository_skills_use_the_cv_namespace(self) -> None:
        skills_root = ROOT / ".agents" / "skills"
        skill_directories = sorted(path for path in skills_root.iterdir() if path.is_dir())

        self.assertGreater(len(skill_directories), 0)
        for skill_directory in skill_directories:
            self.assertTrue(skill_directory.name.startswith("cv-"), skill_directory.name)

            skill_text = (skill_directory / "SKILL.md").read_text(encoding="utf-8")
            name_match = re.search(r"^name:\s*([^\s]+)\s*$", skill_text, re.MULTILINE)
            self.assertIsNotNone(name_match, skill_directory.name)
            self.assertEqual(skill_directory.name, name_match.group(1))

            metadata = (skill_directory / "agents" / "openai.yaml").read_text(
                encoding="utf-8",
            )
            self.assertRegex(metadata, r'(?m)^\s*display_name: "CV ')
            self.assertIn(f"${skill_directory.name}", metadata)


if __name__ == "__main__":
    unittest.main()
