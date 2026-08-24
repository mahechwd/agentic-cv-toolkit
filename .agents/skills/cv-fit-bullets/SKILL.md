---
name: cv-fit-bullets
description: Directly compress, expand, or visually balance one named LaTeX CV bullet block while enforcing a strict two-rendered-line maximum without changing facts. May use explicitly authorised context to add supported detail. Edits only existing resumeItem contents in the selected CV block.
---

# CV fit bullets

Fit selected bullets to the requested rendered space while preserving their strongest meaning.

## Establish the target

- Identify the exact CV path, kind (`experience` or `project`), and target name. Run `python3 scripts/cv_drafts.py list <cv-path>` and require one exact target.
- Read [references/fitting-rules.md](references/fitting-rules.md) completely before editing.
- Determine the requested mode:
  - `one-line`: each selected bullet must render on one line;
  - `preserve-lines`: retain each selected bullet's current rendered line count when it is one or two, and compress any longer bullet to two;
  - `n-lines`: fit each selected bullet to a user-specified line count of one or two;
  - `balanced-lines`: create a controlled ragged-right silhouette with mostly two-line bullets and naturally varied final-line lengths, using visually approved examples as the rhythm reference when supplied; or
  - `page-fit`: keep the whole CV within its existing page limit.
- When the user says “around 112 characters” or “one line” without another limit, use `one-line` with a hard ceiling of 112 visible characters.
- Treat two rendered lines as an absolute maximum in every mode. Reject an `n-lines` request above two and never complete an edit containing a three-line bullet.
- Never edit tracked CVs under `templates/` with personal content.

## Control evidence expansion

- Treat current bullet wording and explicit user facts as the default evidence set. Do not inspect `workspace/context/` merely because a bullet looks sparse.
- When the user explicitly authorises the selected target's context folder, read its non-empty `.md` and `.txt` files and use only relevant supported details to improve visual density. Record every file used for the final report.
- Do not open a PDF unless the user explicitly asks to read PDFs or names that exact PDF. Do not treat an unread file or filename as evidence.
- If the visual-density target cannot be reached from the authorised evidence, do not modify the CV and report the missing factual detail instead of padding or inventing content.

## Capture the baseline and edit directly

1. Read the exact selected block and record its original `\resumeItem{...}` contents, bullet count, surrounding source, and visible character counts.
2. Use a supplied screenshot or compile the current CV to record the actual line count of every selected bullet and total page count. Inspect an existing PDF only when the user explicitly authorises that PDF. For `balanced-lines`, also record the block's line-count profile and each final line's approximate share of the available text width.
3. Preserve every factual element that materially supports the achievement: result, metric, mechanism, technology, scale, and ownership. Mark secondary context as compressible rather than silently dropping it.
4. Construct exactly one replacement for each existing bullet slot, then use `apply_patch` to replace only the inner contents of those `\resumeItem{...}` commands in the selected block.
5. Edit the named CV immediately. Do not create a JSON draft, preview TeX file, review copy, or separate approval step.
6. Do not add, delete, reorder, or move bullet commands. Preserve headings, dates, roles, locations, comments, whitespace outside selected bullet bodies, and every unrelated byte.

## Fit the wording

1. Apply the requested mode and every rule in `references/fitting-rules.md`.
2. Write valid inner LaTeX strings directly into the selected CV bullet bodies.
3. Do not add facts, job-description keywords, new metrics, or stronger ownership.
4. Preserve bullet count and order.
5. For `one-line`, target 105–112 visible characters when supported content fills that space naturally; accept a shorter bullet rather than padding it.
6. For `balanced-lines`, reproduce the approved examples' overall silhouette rather than any single endpoint. Default to mostly two-line bullets with varied final-line fill and allow a rare strong one-line bullet, preferably near the end of the block. Never permit a third line.
7. Keep first and intermediate lines naturally full, let final lines taper, and avoid making several bullets finish at nearly the same horizontal position. Do not alternate lengths mechanically.
8. Expand a visually short bullet only with supported result, mechanism, scale, constraint, or ownership detail. Never add filler or distort an XYZ claim to improve rhythm.
9. For a `balanced-lines` block with at least three two-line bullets, target at least 60% average final-line fill and include at least one fuller ending around 75% or more. Preserve some shorter endings for contrast; do not force every bullet above 60% individually.

## Verify

- Rerun `python3 scripts/cv_drafts.py list <cv-path>` and `python3 scripts/cv_tex.py <cv-path>` after editing. For `one-line`, also pass `--max-chars 112` to `cv_tex.py`.
- Compile the edited CV into an operating-system temporary directory and inspect that rendered output. Do not create repository draft or preview files.
- Verify that every selected bullet occupies no more than two rendered lines, then verify the requested line count and page limit for `page-fit`. For `balanced-lines`, also verify the whole block's ragged-right silhouette, line-count mix, final-line variation, and visual-density floor; character count alone cannot pass this mode.
- Confirm the selected bullet count is unchanged, every bullet is non-empty, LaTeX is balanced, and no content outside the selected `\resumeItem{...}` bodies changed.
- If a selected bullet wraps incorrectly, revise only that bullet and verify again. After three unsuccessful visual fitting attempts, restore the original selected bullet contents if the block has not changed independently, then report which constraint conflicts with the content.
- When rendering is unavailable, stop before editing because the strict two-line maximum cannot be verified. Report the missing renderer instead of creating an estimated draft.

## Report

List the CV path, target, mode, before/after bullets and visible character counts, facts deliberately preserved, facts removed as redundant context, evidence files actually used, final rendered line counts, the approximate final-line-fill pattern and average for `balanced-lines`, and page count when relevant. State that the named CV block was updated directly and can be revised again after the user reviews `workspace/main.tex`.
