#!/usr/bin/env python3
"""Create or explicitly reset the current job-tailored CV."""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path


def prepare_tailored(root: Path, reset: bool = False) -> tuple[Path, str]:
    """Create tailored.tex from main.tex without implicit overwrites."""
    root = root.resolve()
    workspace = root / "workspace"
    canonical_cv = workspace / "main.tex"
    job_description = workspace / "job-description.txt"
    tailored_cv = workspace / "tailored.tex"
    starter_cv = root / "templates" / "main.tex"

    if not canonical_cv.is_file() or canonical_cv.stat().st_size == 0:
        raise ValueError("workspace/main.tex is missing or empty")
    if not job_description.is_file() or job_description.stat().st_size == 0:
        raise ValueError("workspace/job-description.txt is missing or empty")
    if tailored_cv.exists() and not tailored_cv.is_file():
        raise IsADirectoryError(f"expected private file: {tailored_cv}")

    if tailored_cv.exists() and not reset:
        if (
            starter_cv.is_file()
            and tailored_cv.read_bytes() == starter_cv.read_bytes()
            and canonical_cv.read_bytes() != starter_cv.read_bytes()
        ):
            shutil.copy2(canonical_cv, tailored_cv)
            return tailored_cv, "refreshed untouched starter from main"
        return tailored_cv, "kept existing"

    shutil.copy2(canonical_cv, tailored_cv)
    return tailored_cv, "reset from main" if reset else "created from main"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Create workspace/tailored.tex from the canonical CV",
    )
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Explicitly replace tailored.tex with the current main.tex",
    )
    parser.add_argument("--root", type=Path, default=Path.cwd())
    args = parser.parse_args()

    try:
        path, status = prepare_tailored(args.root, reset=args.reset)
    except (OSError, ValueError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 2

    print(f"{path}: {status}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
