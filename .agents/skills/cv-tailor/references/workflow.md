# Operating procedure

All commands run from the skill's repository root. Python 3.10+ is required. The render helper also needs `pdfplumber`, `pdftoppm`, and an existing `pdflatex`, `xelatex`, or `lualatex`. Prefer available bundled Python dependencies; use the workspace dependency tool if needed. Compiler installation is a setup dependency: if unavailable, report the missing dependency and preserve the destination.

## Preflight and selection

```sh
python3 scripts/cv_tailor.py check 'Example Labs' 'section:Projects'
```

With no targets, `check` still checks the JD/state before reporting that selection is required. Use `python3 scripts/cv_parser.py list workspace/main.tex --json` for ambiguous names. Entry targets match an exact heading field or current parser ID. For decorated project titles, use the ID after resolving the user's intended project. IDs are valid only for the current source snapshot.

The check output includes selected canonical bullet IDs and bodies. Do not publish this private output outside the task. Research and draft only after preflight passes.

If the existing tailored file has no state or has been manually edited, report it and let the user decide how to handle that copy. Do not delete it or infer a prior JD. A missing/empty destination is normal first use. A valid different JD stages an automatic reset.

## Prepare

Write a private JSON object mapping **every selected canonical bullet ID** to its final LaTeX body, including unchanged bullets. Use a JSON serializer, not shell interpolation. Store it in a private temporary directory with restricted permissions. Escape text characters (`%`, `&`, `_`, `#`, `$`) for LaTeX and use supported inline formatting. The helper rejects layout/structural commands and reparses the candidate. Unchanged original formatting is preserved.

```sh
python3 scripts/cv_tailor.py prepare /absolute/private/replacements.json 'Example Labs' 'section:Projects'
```

This prints a newly created private session directory. It contains `candidate.tex` and `manifest.json`. Inspect the diff against the current destination: only selected bodies, necessary selected bullet-slot synchronisation, and the leading state comment should differ, unless a JD reset was staged. When selected bullet counts differ, the helper copies the canonical direct bullet run automatically. Missing/ambiguous corresponding entries or interleaved unsupported structures stop safely.

Revisions use the same targets and session:

```sh
python3 scripts/cv_tailor.py prepare /absolute/private/replacements.json 'Example Labs' 'section:Projects' --session /absolute/session
```

For identical candidate and destination bytes, use `publish` with an empty JSON object to confirm unchanged; no rendering is needed.

## Compile and inspect

```sh
python3 scripts/cv_tailor_render.py /absolute/session --engine pdflatex
```

Select the engine from the template/user's known Overleaf settings; ask only if uncertain and material. Do not silently change fonts or template layout. Two compiler passes run together; private logs record errors. Relative dependencies resolve from the original workspace. Outputs include `candidate.pdf`, `page-*.png`, `coordinates.json`, and `compilation.json` with hashes, compiler/version, dependencies, and elapsed duration. Do not promise a fixed compile time.

Inspect the actual page images with an image-viewing tool. Use PDF word coordinates to identify each bullet by entry heading, source order, and text, not a global match that could confuse repeated wording. Combine bold/font fragments on the same baseline. Check wrapped hyphenation and page transitions explicitly. If mapping is uncertain, fail the review.

For each selected canonical bullet ID, count distinct rendered text baselines and measure final-line fullness: `(last text x - text left edge) / available text width`. Derive available width from actual template geometry and confirm it against the image, not from the longest observed line. Exclude bullet glyphs. Inspect the complete entry for short overflow, uneven balance, clipping, and overlap. Inspect changed-JD output as a whole as well.

Create private `review.json` using the exact hashes from compilation.json:

```json
{
  "candidate_sha256": "actual candidate hash",
  "pdf_sha256": "actual PDF hash",
  "images_inspected": true,
  "balanced": true,
  "bullets": {
    "actual canonical bullet ID": {
      "lines": 2,
      "final_line_fill": 0.68,
      "mapping_confident": true
    }
  }
}
```

Values above illustrate the schema; measure actual values. Include all selected IDs. The receipt records agent observations, not an independent automated layout guarantee. Write `balanced: false` or `mapping_confident: false` for failed reviews and submit them to `publish` so the failure is counted. Never edit the failure counter or create another session to evade the three-round limit. Fix all selected changes together for the next round.

## Publish

```sh
python3 scripts/cv_tailor.py publish /absolute/session /absolute/session/review.json
```

Publication checks source hashes, candidate reconstruction, PDF hashes, dependency hashes, review completeness and line limits, then atomically replaces only `workspace/tailored.tex`. Its leading comment holds normalised JD and body hashes so metadata and output cannot be saved separately. Concurrent cooperating writers are locked. If a lock remains after a crash, investigate before removing it.

A failed review leaves the destination intact. Do not bypass a failure with direct edits. Preserve private diagnostic artifacts when useful, otherwise remove only the temporary session and drafting files created for this request after delivery.
