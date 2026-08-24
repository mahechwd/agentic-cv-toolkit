#!/usr/bin/env python3
"""Create a private, non-destructive CV workspace for one application."""

from __future__ import annotations

import argparse
import re
import shutil
import sys
from pathlib import Path


SLUG_PATTERN = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")


def prepare_application(root: Path, slug: str) -> Path:
    if not SLUG_PATTERN.fullmatch(slug):
        raise ValueError("slug must contain lowercase letters, digits, and single hyphens")

    root = root.resolve()
    canonical_cv = root / "workspace" / "main.tex"
    job_description = root / "workspace" / "job-description.txt"
    destination = root / "applications" / slug

    if not canonical_cv.is_file() or canonical_cv.stat().st_size == 0:
        raise ValueError("workspace/main.tex is missing or empty")
    if not job_description.is_file() or job_description.stat().st_size == 0:
        raise ValueError("workspace/job-description.txt is missing or empty")
    if destination.exists():
        raise FileExistsError(f"refusing to overwrite existing application workspace: {destination}")

    destination.mkdir(parents=True)
    shutil.copy2(canonical_cv, destination / "main.tex")
    shutil.copy2(canonical_cv, destination / "main.source.tex")
    shutil.copy2(job_description, destination / "job-description.txt")
    return destination


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("slug", help="Lowercase company-role slug")
    parser.add_argument("--root", type=Path, default=Path.cwd())
    args = parser.parse_args()

    try:
        destination = prepare_application(args.root, args.slug)
    except FileExistsError as error:
        print(f"error: {error}", file=sys.stderr)
        return 1
    except (OSError, ValueError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 2
    print(destination)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
