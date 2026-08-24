---
name: cv-tailor-bullets
description: Draft truthful job-specific rewrites for one named Experience or Projects block in a private application CV, using only supported keywords while preserving bullet count and footprint. May apply its own exact draft when explicitly requested.
---

# CV tailor bullets

Create a truthful, job-specific application CV without mutating the canonical CV.

## Required inputs

- Locate non-empty `workspace/main.tex` and `workspace/job-description.txt`.
- Obtain an explicit kind (`experience` or `project`) and target name for this tailoring pass.
- Read [references/tailoring-rules.md](references/tailoring-rules.md) completely before analysis or editing.
- Identify the company and role from the job description. If either is genuinely ambiguous, ask for the missing value rather than inventing a slug.
- Convert them to a lowercase hyphenated `<company>-<role>` slug.

## Create or select the application copy

1. If `applications/<slug>/` does not exist, run `python3 scripts/prepare_application.py <slug>` from the repository root.
2. If the application copy already exists, never overwrite it with canonical `workspace/main.tex`. Confirm that its `job-description.txt` is the intended vacancy and work only in its `main.tex`.
3. Never tailor canonical `workspace/main.tex` or any tracked file under `templates/`.
4. Treat `applications/<slug>/main.source.tex` as the immutable baseline. Run `python3 scripts/cv_drafts.py list applications/<slug>/main.tex` and require one exact target.
5. Initialise `drafts/tailor/<slug>-<target>.json` against the application `main.tex` with `python3 scripts/cv_drafts.py init`. Do not overwrite an existing draft.

## Build the keyword evidence map

1. Extract the job's must-have qualifications, preferred qualifications, responsibilities, technologies, domain language, and behavioural expectations.
2. Classify each meaningful term as:
   - already represented;
   - supported but absent;
   - supported but underrepresented; or
   - unsupported gap.
3. A bullet-level technology or method is supported only by the relevant `workspace/context/` evidence, an explicit user fact, or equivalent wording already in that bullet. A name in the skills section alone does not prove it was used for a specific achievement.
4. Read every supported evidence file for each experience or project whose bullets may change. Track the source for every proposed insertion.
5. Never insert unsupported gaps. Report them honestly instead.

## Draft safely

1. Rewrite only bullets that materially improve relevance, clarity, credibility, or scanability.
2. Apply all rules in `references/tailoring-rules.md`.
3. Write only inner LaTeX strings to `proposed_bullets`; preserve bullet count and order.
4. Preserve each edited bullet's rendered line count. Use a visible-character delta of at most three as the fallback constraint until PDF rendering confirms the actual footprint.
5. If a supported keyword cannot fit naturally without weakening the claim or footprint, retain the existing proposal and report the trade-off.
6. Record evidence paths and notes in the draft. Keep status as `draft` and do not edit the application CV.

## Verify and report

- Run `python3 scripts/cv_drafts.py show <draft-path>` and create a preview with `python3 scripts/cv_drafts.py preview --cv applications/<slug>/main.tex --draft <draft-path> --output drafts/previews/<slug>-<target>.tex`.
- Compare the preview with the application baseline using `python3 scripts/cv_tex.py <preview-path> --compare applications/<slug>/main.tex --tolerance 3` when bullet order and count remain aligned.
- Compile and inspect the preview PDF when a LaTeX toolchain is available. Confirm unchanged line counts and a one-page final CV when that was already the baseline.
- If rendering is unavailable, state that line-count equality is estimated rather than verified.
- Report the application and draft paths, target, proposed changes, supported keywords added, evidence for each addition, unsupported gaps left out, character deltas, and visual-verification status. If the user explicitly asks this skill to apply that exact draft, show it once, set its status to `approved`, and run `python3 scripts/cv_drafts.py apply`; do not require another skill.
