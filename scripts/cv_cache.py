#!/usr/bin/env python3
"""Keep a private parsed CV snapshot fresh using source and parser fingerprints."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import tempfile
from dataclasses import asdict
from pathlib import Path

from cv_blocks import scan_targets
from cv_tex import extract_bullets


ROOT = Path(__file__).resolve().parents[1]
SCHEMA_VERSION = 1
PARSER_FILES = tuple(ROOT / "scripts" / name for name in ("cv_tex.py", "cv_blocks.py", "cv_cache.py"))

def digest_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def parser_fingerprint() -> str:
    """Changes to any parser helper or the cache schema invalidate snapshots."""
    digest = hashlib.sha256(str(SCHEMA_VERSION).encode("ascii"))
    for path in PARSER_FILES:
        digest.update(path.name.encode("utf-8"))
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def cache_path_for(cv: Path, cache_dir: Path | None = None) -> Path:
    location = cache_dir if cache_dir is not None else ROOT / "workspace" / ".cache" / "cv"
    identity = digest_bytes(str(cv.resolve()).encode("utf-8"))[:16]
    return location / f"{cv.stem}-{identity}.parsed.json"


def parse_snapshot(source: bytes) -> dict[str, object]:
    """Every extraction reads the same immutable, private source snapshot."""
    with tempfile.TemporaryDirectory(prefix="cv-parse-") as directory:
        snapshot = Path(directory) / "snapshot.tex"
        snapshot.write_bytes(source)
        targets = scan_targets(snapshot)
        bullets = extract_bullets(snapshot)
    # Semantic review gets text and exact names, never edit offsets or bold spans.
    content = {"targets": [
        {"kind": target.kind, "name": target.name, "context": target.context,
         "bullets": [bullet.rendered for bullet in target.bullets]}
        for target in targets
    ]}
    return {
        "content": content,
        "edit": {"targets": [{**asdict(target), "bullets": [asdict(bullet) for bullet in target.bullets]} for target in targets],
                 "bullets": [asdict(bullet) for bullet in bullets]},
    }


def _payload_digest(payload: dict[str, object]) -> str:
    return digest_bytes(json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8"))


def _load_cache(path: Path, cv: Path, source_hash: str, parser_hash: str) -> dict[str, object] | None:
    try:
        document = json.loads(path.read_text(encoding="utf-8"))
        if (document["schema_version"] != SCHEMA_VERSION
                or document["source"] != {"path": str(cv), "sha256": source_hash}
                or document["parser_sha256"] != parser_hash):
            return None
        payload = document["parsed"]
        if not isinstance(payload, dict) or set(payload) != {"content", "edit"}:
            return None
        if document["payload_sha256"] != _payload_digest(payload):
            return None
        return document
    except (OSError, UnicodeError, ValueError, KeyError, TypeError):
        return None


def _write_cache(path: Path, document: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary: str | None = None
    try:
        with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=path.parent,
                                         prefix=".cv-", suffix=".tmp", delete=False) as handle:
            temporary = handle.name
            json.dump(document, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        if temporary is not None:
            Path(temporary).unlink(missing_ok=True)


def ensure_parsed(cv: Path, *, cache_dir: Path | None = None) -> tuple[dict[str, object], str, Path]:
    """Return a verified snapshot; never serve a stale cache after a failure."""
    cv = cv.resolve()
    cache_path = cache_path_for(cv, cache_dir)
    try:
        source = cv.read_bytes()
        source_hash = digest_bytes(source)
        parser_hash = parser_fingerprint()
        document = _load_cache(cache_path, cv, source_hash, parser_hash)
        status = "reused"
        if document is None:
            payload = parse_snapshot(source)
            document = {
                "schema_version": SCHEMA_VERSION,
                "source": {"path": str(cv), "sha256": source_hash},
                "parser_sha256": parser_hash,
                "payload_sha256": _payload_digest(payload),
                "parsed": payload,
            }
            status = "rebuilt"
        if cv.read_bytes() != source or parser_fingerprint() != parser_hash:
            raise ValueError("CV or parser changed during parsing; rerun before using the snapshot")
        if status == "rebuilt":
            _write_cache(cache_path, document)
        return document, status, cache_path
    except (OSError, UnicodeError, ValueError):
        cache_path.unlink(missing_ok=True)
        raise


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("cv", type=Path)
    parser.add_argument("--view", choices=("summary", "content", "edit"), default="summary")
    parser.add_argument("--cache-dir", type=Path, help="Private cache directory; defaults to ignored workspace/.cache/cv")
    args = parser.parse_args()
    try:
        document, status, cache_path = ensure_parsed(args.cv, cache_dir=args.cache_dir)
    except (OSError, UnicodeError, ValueError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 2
    output = {"cv": document["source"]["path"], "source_sha256": document["source"]["sha256"],
              "parser_sha256": document["parser_sha256"], "cache": str(cache_path), "status": status}
    if args.view == "content":
        output["content"] = document["parsed"]["content"]
    elif args.view == "edit":
        output["parsed"] = document["parsed"]
    print(json.dumps(output, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
