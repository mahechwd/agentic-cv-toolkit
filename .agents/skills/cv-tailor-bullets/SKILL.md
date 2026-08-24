---
name: cv-tailor-bullets
description: Directly tailor one named Experience or Projects block in workspace/tailored.tex with supported ATS-relevant terms from the current job description while preserving bullet count and footprint. Preserves exact per-bullet length only when explicitly requested. Never edits canonical workspace/main.tex.
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
7. Rank supported ATS-relevant terms by job-description importance: required qualifications and repeated must-haves first, then core responsibilities, named technologies or practices, and precise domain terminology. Ignore company slogans, generic filler, and unsupported terms.
8. Select the footprint mode before editing:
   - **Default mode:** use this unless the user explicitly asks to keep bullet lengths the same.
   - **Exact-length mode:** activate only when the user says, for example, “keep the length the same”, “same character count”, “exact length”, “fixed length”, or “zero delta”. Do not infer this mode merely from a request to preserve layout or keep bullets concise.

## Tailor directly

1. Record the complete canonical CV before editing so any accidental change to it can be detected.
2. Record the selected tailored block's bullet bodies, count, surrounding source, rendered line counts when available, and per-bullet visible character counts from `python3 scripts/cv_blocks.py list workspace/tailored.tex --json`.
3. Rewrite only bullets that materially improve job relevance, clarity, credibility, or scanability, applying every rule in `references/tailoring-rules.md`.
4. Use only supported terminology. Prefer the job description's exact standard term over a weaker synonym when both have the same substantive meaning. Leave unsupported requirements as honest gaps.
5. In default mode, preserve the rendered footprint using the original rules: retain every edited bullet's rendered line count, or keep its visible-character delta within three when rendering is unavailable.
6. In exact-length mode, preserve each corresponding bullet's exact visible character count. Do not transfer character budget between bullets. Rewrite surrounding supported wording only when needed to fit a useful term naturally at zero character delta.
7. In either mode, leave a bullet unchanged and report the omitted term when it cannot fit truthfully, naturally, and within the active footprint constraint. Never pad with filler or force an awkward synonym merely to satisfy length.
8. Use `apply_patch` to replace only the inner contents of existing `\resumeItem{...}` commands in the selected block of `workspace/tailored.tex`.
9. Preserve bullet count, order, rendered line count, headings, roles, dates, locations, comments, whitespace outside selected bullet bodies, and every unrelated byte.
10. Do not create JSON drafts, preview TeX files, application folders, or a separate approval step.

## Verify and report

- Rerun `python3 scripts/cv_blocks.py list workspace/tailored.tex`, `python3 scripts/cv_blocks.py list workspace/tailored.tex --json`, and `python3 scripts/cv_tex.py workspace/tailored.tex`.
- Confirm `workspace/main.tex` is byte-for-byte unchanged and only the selected tailored bullet bodies changed.
- Verify the active footprint mode:
  - **Default mode:** preserve each edited bullet's rendered line count. Compile and inspect when a LaTeX renderer is available; otherwise require an absolute visible-character delta of at most three and state that line equality is estimated.
  - **Exact-length mode:** compare the selected target's before/after character arrays. Every corresponding delta must be exactly zero; a block average is not sufficient. Also preserve rendered line count when a renderer is available. Without one, report that exact character counts were verified but wrapping remains unverified.
- Confirm every inserted ATS-relevant term is important to the job description, reads naturally, and is supported by current wording, an explicit user fact, or an authorised evidence file.
- Do not claim guaranteed performance in a company's private ATS.
- Report the target, active footprint mode, before/after bullets, exact supported terms added, supported terms omitted because they could not fit naturally, evidence used, unsupported gaps omitted, per-bullet character deltas, and rendering status. In exact-length mode, all deltas must be `0`. State that `workspace/tailored.tex` was updated directly and `workspace/main.tex` was not modified.
