---
name: cv-tailor-bullets
description: Directly tailor one named Experience or Projects block in workspace/tailored.tex for the current job description, using only supported keywords while preserving bullet count and footprint. Never edits canonical workspace/main.tex.
---

# CV tailor bullets

Create the current job-specific CV in `workspace/tailored.tex` while keeping `workspace/main.tex` canonical and unchanged.

## Establish the two-file workflow

- Require non-empty `workspace/main.tex` and `workspace/job-description.txt`.
- Run `python3 scripts/prepare_tailored.py` before tailoring. It creates a missing copy from the canonical CV, refreshes an untouched starter after the user pastes their real CV, and preserves existing tailored work.
- Preserve an existing `workspace/tailored.tex` across follow-up tailoring passes. Never replace it merely because `workspace/main.tex` has changed.
- Run `python3 scripts/prepare_tailored.py --reset` only when the user explicitly asks to reset, start fresh, or begin tailoring for a new job description. State that this discards the previous tailored CV before running it.
- Never edit `workspace/main.tex` or a tracked file under `templates/`.

## Select the target and evidence

1. Obtain an explicit kind (`experience` or `project`) and exact target name.
2. Read [references/tailoring-rules.md](references/tailoring-rules.md) completely before editing.
3. Run `python3 scripts/cv_blocks.py list workspace/tailored.tex` and require one exact target.
4. Treat the target's current bullet wording and explicit user facts as the default evidence set.
5. Do not inspect `workspace/context/` unless the user explicitly authorises relevant files or the target folder. A folder request permits non-empty `.md` and `.txt` files only; read a PDF only when the user explicitly names it or asks to read PDFs.
6. Classify important job terms as already represented, supported but absent, supported but underrepresented, or unsupported. A skills-section keyword alone does not prove it was used in a specific achievement.

## Tailor directly

1. Record the complete canonical CV before editing so any accidental change to it can be detected.
2. Record the selected tailored block's bullet bodies, count, surrounding source, and visible character counts.
3. Rewrite only bullets that materially improve job relevance, clarity, credibility, or scanability, applying every rule in `references/tailoring-rules.md`.
4. Use only supported terminology. Leave unsupported requirements as honest gaps.
5. Use `apply_patch` to replace only the inner contents of existing `\resumeItem{...}` commands in the selected block of `workspace/tailored.tex`.
6. Preserve bullet count, order, headings, roles, dates, locations, comments, whitespace outside selected bullet bodies, and every unrelated byte.
7. Do not create JSON drafts, preview TeX files, application folders, or a separate approval step.

## Verify and report

- Rerun `python3 scripts/cv_blocks.py list workspace/tailored.tex` and `python3 scripts/cv_tex.py workspace/tailored.tex`.
- Confirm `workspace/main.tex` is byte-for-byte unchanged and only the selected tailored bullet bodies changed.
- Preserve each edited bullet's rendered line count. Compile and inspect the tailored CV when a LaTeX renderer is available; otherwise use a visible-character delta of at most three as the fallback and state that line equality is estimated.
- Confirm every inserted keyword is supported by current wording, an explicit user fact, or an authorised evidence file.
- Report the target, before/after bullets, supported terms added, evidence used, unsupported gaps omitted, character deltas, and rendering status. State that `workspace/tailored.tex` was updated directly and `workspace/main.tex` was not modified.
