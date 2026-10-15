"""Reset the private CV workspace, deleting all existing workspace content."""

from pathlib import Path
import shutil


def setup_workspace(root: Path) -> list[Path]:
    """Delete the existing workspace and create an empty replacement."""
    workspace = root / "workspace"
    if workspace.is_symlink():
        workspace.unlink()
    elif workspace.is_dir():
        shutil.rmtree(workspace)
    elif workspace.exists():
        workspace.unlink()
    created = []
    for relative in ("cv-context/experience", "cv-context/projects"):
        directory = workspace / relative
        directory.mkdir(parents=True, exist_ok=True)
        created.append(directory)
    for name in ("main.tex", "tailored.tex", "job-description.txt"):
        path = workspace / name
        path.write_text("", encoding="utf-8")
        created.append(path)
    return created


def main() -> None:
    root = Path(__file__).resolve().parent.parent
    for path in setup_workspace(root):
        print(f"Created {path.relative_to(root)}")
    print("Workspace reset. All previous workspace content has been deleted.")
    print("Paste your LaTeX CV into workspace/main.tex.")
    print("Optionally add supporting documents under workspace/cv-context/.")


if __name__ == "__main__":
    main()
