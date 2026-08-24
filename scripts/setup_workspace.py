#!/usr/bin/env python3
"""Create or migrate the ignored private CV workspace."""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path


TEMPLATE_DIRECTORY = "templates"
WORKSPACE_DIRECTORY = "workspace"
FILE_TEMPLATES = ("main.tex", "job-description.txt")
DIRECTORY_TEMPLATES = ("context",)
LEGACY_INPUTS = {
    "main.tex": "main.tex",
    "job-description.txt": "job-description.txt",
    "cv-context": "context",
}


def setup_workspace(root: Path) -> dict[str, str]:
    """Create missing inputs and safely migrate the previous root layout."""
    root = root.resolve()
    templates = root / TEMPLATE_DIRECTORY
    workspace = root / WORKSPACE_DIRECTORY
    results: dict[str, str] = {}

    for name in FILE_TEMPLATES:
        source = templates / name
        if not source.is_file():
            raise FileNotFoundError(f"missing tracked template: {source}")
    for name in DIRECTORY_TEMPLATES:
        source = templates / name
        if not source.is_dir():
            raise FileNotFoundError(f"missing tracked template directory: {source}")

    workspace.mkdir(exist_ok=True)

    for legacy_name, destination_name in LEGACY_INPUTS.items():
        source = root / legacy_name
        destination = workspace / destination_name
        result_name = str(destination.relative_to(root))
        if destination.exists():
            if destination_name in DIRECTORY_TEMPLATES and not destination.is_dir():
                raise NotADirectoryError(f"expected private directory: {destination}")
            if destination_name not in DIRECTORY_TEMPLATES and not destination.is_file():
                raise IsADirectoryError(f"expected private file: {destination}")
            suffix = "/" if destination.is_dir() else ""
            results[result_name + suffix] = "kept existing"
            continue
        if source.exists():
            shutil.move(str(source), str(destination))
            suffix = "/" if destination.is_dir() else ""
            results[result_name + suffix] = "migrated legacy input"

    for name in FILE_TEMPLATES:
        source = templates / name
        destination = workspace / name
        result_name = str(destination.relative_to(root))
        if destination.exists():
            if not destination.is_file():
                raise IsADirectoryError(f"expected private file: {destination}")
            results.setdefault(result_name, "kept existing")
            continue
        shutil.copy2(source, destination)
        results[result_name] = "created from template"

    for name in DIRECTORY_TEMPLATES:
        source = templates / name
        destination = workspace / name
        result_name = f"{destination.relative_to(root)}/"
        if destination.exists():
            if not destination.is_dir():
                raise NotADirectoryError(f"expected private directory: {destination}")
            results.setdefault(result_name, "kept existing")
            continue
        shutil.copytree(source, destination)
        results[result_name] = "created from template"

    tailored = workspace / "tailored.tex"
    tailored_result_name = str(tailored.relative_to(root))
    if tailored.exists():
        if not tailored.is_file():
            raise IsADirectoryError(f"expected private file: {tailored}")
        results[tailored_result_name] = "kept existing"
    else:
        shutil.copy2(workspace / "main.tex", tailored)
        results[tailored_result_name] = "created from main"

    return results


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Create or migrate the ignored workspace/ CV inputs",
    )
    parser.add_argument("--root", type=Path, default=Path.cwd())
    args = parser.parse_args()

    try:
        results = setup_workspace(args.root)
    except OSError as error:
        print(f"error: {error}", file=sys.stderr)
        return 2

    for path, status in results.items():
        print(f"{path}: {status}")
    print("Tracked templates/ files were not modified.")
    print("Next: paste your LaTeX CV into workspace/main.tex.")
    print("Next: paste one complete vacancy into workspace/job-description.txt.")
    print("Next: tailor only workspace/tailored.tex; reset it explicitly for a new job.")
    print("Next: add evidence under workspace/context/experience/ or workspace/context/projects/.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
