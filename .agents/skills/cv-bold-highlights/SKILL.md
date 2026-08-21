---
name: cv-bold-highlights
description: Directly add sparse LaTeX textbf emphasis to one named CV bullet block's most important existing metrics and supported technologies without changing visible wording or rendered line count. Edits only existing resumeItem contents in the selected CV block.
---

# CV bold highlights

Add restrained `\textbf{...}` emphasis while keeping the visible CV text identical.

## Select scope

- Identify the exact CV path, kind (`experience` or `project`), and target name. Run `python3 scripts/cv_drafts.py list <cv-path>` and require one exact target.
- Read [references/bolding-rules.md](references/bolding-rules.md) completely before editing.
- Read the exact selected block and record its original `\resumeItem{...}` contents, bullet count, visible wording, character counts, and surrounding source.
- Compile the current CV into an operating-system temporary directory and record each selected bullet's rendered line count and total page count. Stop before editing when rendering is unavailable.
- Never edit tracked example CVs with personal content.

## Choose highlights

1. Read each bullet as a recruiter scanning for outcome, scale, and technical fit.
2. Select semantic anchors rather than enforcing a per-bullet quota, prioritising:
   - a decision-relevant metric with its meaningful unit or scale noun;
   - a differentiating mechanism, architecture, or delivered capability;
   - a supported technology, framework, method, or system term central to the achievement; and
   - a concise external validation signal such as an award when it materially strengthens the bullet.
3. Apply every rule in `references/bolding-rules.md`.
4. Do not change, add, remove, reorder, or re-punctuate visible wording.

## Edit directly

1. Construct exactly one formatted replacement for each existing bullet slot. Wrap selected spans only with `\textbf{...}` and retain required LaTeX escapes inside the command, such as `\textbf{30\%}`.
2. Use `apply_patch` to replace only the inner contents of the selected block's existing `\resumeItem{...}` commands. Do not create a JSON draft, preview TeX file, review copy, or separate approval step.
3. Keep bullet count, order, visible wording, punctuation, and whitespace-normalised text unchanged. Preserve headings, dates, roles, locations, comments, whitespace outside selected bullet bodies, and every unrelated byte.

## Verify

1. Rerun `python3 scripts/cv_drafts.py list <cv-path>` and `python3 scripts/cv_tex.py <cv-path>` after editing. Compare every selected bullet's rendered text with the recorded baseline; it must be identical.
2. Compile the edited CV into an operating-system temporary directory and inspect it. Every selected bullet must retain its original rendered line count, the CV must retain its page count, and no bullet may exceed two rendered lines.
3. If bolding creates a new wrap or page overflow, remove the lower-priority highlight rather than rewriting content. Leave a bullet unbolded when no highlight fits safely.
4. Confirm LaTeX is balanced and no content outside the selected `\resumeItem{...}` bodies changed.
5. If verification still fails after removing unsafe highlights, restore the original selected bullet contents if the block has not changed independently and report the conflict.

## Report

List the CV path and target; each applied bold span and why it is scan-worthy; confirmation that visible wording, bullet count, rendered line counts, and page count are unchanged; and any bullet deliberately left unbolded. State that the named CV block was updated directly and can be revised again after the user reviews `main.tex`.
