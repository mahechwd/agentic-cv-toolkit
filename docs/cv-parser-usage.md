# Read-only CV parser

Requires Python 3.10 or newer and only the standard library. Use a supported Jake-style LaTeX source; see [parser rules](cv-parser.md) and [output contract](cv-parser-output.md).

## Commands

From the repository root:

```bash
# Readable full CV; defaults to this checkout's workspace/main.tex.
python3 scripts/cv_parser.py inspect

# Complete JSON: source identity, structure, raw text, readable text, locations.
python3 scripts/cv_parser.py inspect workspace/main.tex --json

# List all entries, including education and nested roles.
python3 scripts/cv_parser.py list workspace/main.tex
python3 scripts/cv_parser.py list workspace/tailored.tex --json

# Inspect a synthetic example without creating any cache.
python3 scripts/cv_parser.py inspect tests/fixtures/parser/synthetic.tex --no-cache
```

The script can be invoked by absolute path from another directory. An omitted source always refers to this checkout's workspace; an explicit relative source is relative to the caller's current directory. Module invocation (`python3 -m scripts.cv_parser`) is also supported from the repository root.

`list` reports each snapshot-local ID, section, parent ID in JSON, heading, direct bullet count, empty bullet count, and source line. Duplicate names stay separate; this command does not choose a target for the user. IDs must be interpreted with the source hash and are not durable across structural changes.

## Results and failures

- Success: exit 0; requested text or JSON on stdout.
- Input, syntax, extraction, or source-change failure: exit 1; a JSON error diagnostic on stderr, no partial stdout.
- Invalid CLI arguments: argparse usage error, exit 2.
- Cache-write failure: exit 0 with current in-memory data and a warning on stderr. Do not use an old disk text view after a warning.

Both commands preserve the source. By default they save validated private derived data under `workspace/.cache/cv/`. Only main.tex and tailored.tex directly under workspace support caching. `--no-cache` performs no cache reads or writes and supports arbitrary input paths. Existing context documents are never opened.

Do not run the workspace setup command merely to use the parser: setup intentionally deletes all existing workspace content.

## Verification and boundaries

```bash
python3 -m unittest discover -s tests -v
```

Tests cover exact synthetic output, original-byte preservation, syntax failures, Unicode locations, cache invalidation and interrupted writes, and subprocess CLI workflows. Unknown visible syntax is reported instead of silently omitted. The supported macro vocabulary is deliberately bounded; this tool does not execute TeX, render PDFs, measure line lengths, edit bullets, or implement a skill.
