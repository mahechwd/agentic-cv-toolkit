import importlib.util
from pathlib import Path
import tempfile
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / "scripts/setup_workspace.py"
spec = importlib.util.spec_from_file_location("setup_workspace", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class SetupWorkspaceTests(unittest.TestCase):
    def assert_empty_workspace(self, root):
        workspace = root / "workspace"
        expected = {
            "main.tex", "tailored.tex", "job-description.txt", "cv-context",
            "cv-context/experience", "cv-context/projects",
        }
        self.assertEqual({str(p.relative_to(workspace)) for p in workspace.rglob("*")}, expected)
        for name in ("main.tex", "tailored.tex", "job-description.txt"):
            self.assertEqual((workspace / name).read_bytes(), b"")

    def test_creates_then_resets_all_workspace_content(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            outside = root / "keep.txt"
            outside.write_text("Keep this")
            module.setup_workspace(root)
            self.assert_empty_workspace(root)
            workspace = root / "workspace"
            for name in ("main.tex", "tailored.tex", "job-description.txt"):
                (workspace / name).write_text("Previous content")
            for kind in ("experience", "projects"):
                evidence = workspace / "cv-context" / kind / "example" / "notes.txt"
                evidence.parent.mkdir()
                evidence.write_text("Previous evidence")
            (workspace / "extra.txt").write_text("Extra content")
            module.setup_workspace(root)
            self.assert_empty_workspace(root)
            self.assertEqual(outside.read_text(), "Keep this")

    def test_workspace_symlink_does_not_delete_target(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            target = root / "outside"
            target.mkdir()
            (target / "keep.txt").write_text("Keep this")
            (root / "workspace").symlink_to(target, target_is_directory=True)
            module.setup_workspace(root)
            self.assert_empty_workspace(root)
            self.assertFalse((root / "workspace").is_symlink())
            self.assertEqual((target / "keep.txt").read_text(), "Keep this")


if __name__ == "__main__":
    unittest.main()
