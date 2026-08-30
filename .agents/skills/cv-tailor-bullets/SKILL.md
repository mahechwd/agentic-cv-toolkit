---
name: cv-tailor-bullets
description: Directly tailor one named Experience or Projects block in workspace/tailored.tex by auditing the current version, comparing canonical evidence, applying supported ATS-relevant job language, and rebalancing bold emphasis for the vacancy. Optionally research the hiring company when explicitly requested. Preserves exact per-bullet length only when explicitly requested and never edits workspace/main.tex.
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
4. Read the whole job description and audit the selected tailored block before consulting its canonical counterpart. Identify achievements already worth retaining, weak or generic wording, missing supported requirements, duplicated signals, and any tailoring that weakened a strong fact.
5. Run `python3 scripts/cv_blocks.py list workspace/main.tex` and inspect only the matching kind and exact target name when it exists. Treat it as a read-only evidence reservoir: identify stronger metrics, technical decisions, ownership, scale, or achievements that are absent or weakened in the tailored block. If no matching canonical target exists, continue from the tailored evidence and report that comparison was unavailable.
6. Use the current tailored target, its matching canonical target, and explicit user facts as the default candidate-evidence set. Never assume canonical wording is stronger or replace the tailored block wholesale.
7. Do not inspect `workspace/context/` unless the user explicitly authorises relevant files or the target folder. A folder request permits non-empty `.md` and `.txt` files only; read a PDF only when the user explicitly names it or asks to read PDFs.
8. Build a job-requirement map covering must-haves, core responsibilities, named technologies or practices, domain terminology, and preferred requirements. Classify each important term as present in tailored, supported by canonical evidence but absent, supported but underrepresented, or unsupported. A skills-section keyword alone does not prove it was used in a specific achievement.
9. Rank supported ATS-relevant terms by job-description importance: required qualifications and repeated must-haves first, then core responsibilities, named technologies or practices, and precise domain terminology. Ignore company slogans, generic filler, and unsupported terms.
10. Select company-research mode:
   - **Default:** do not browse for company information.
   - **Research mode:** activate only when the user explicitly asks to research the company or employer. Use current official company sources first—such as the vacancy, careers, product, engineering, security, and about pages—and cite the sources used. If the hiring company cannot be identified confidently, ask rather than researching a similarly named organisation.
   - Use research only to prioritise already-supported achievements and understand product, customer, domain, or engineering concerns. Never use company material as evidence that the candidate has a skill or performed an achievement.
11. Select the footprint mode before editing:
   - **Default mode:** use this unless the user explicitly asks to keep bullet lengths the same.
   - **Exact-length mode:** activate only when the user says, for example, “keep the length the same”, “same character count”, “exact length”, “fixed length”, or “zero delta”. Do not infer this mode merely from a request to preserve layout or keep bullets concise.

## Tailor directly

1. Record the complete canonical CV before editing so any accidental change to it can be detected.
2. Record the selected tailored block's bullet bodies, count, surrounding source, rendered line counts when available, and per-bullet visible character counts from `python3 scripts/cv_blocks.py list workspace/tailored.tex --json`.
3. Evaluate each existing tailored bullet against the job-requirement map and combined evidence. Retain it unchanged when it is already the strongest truthful use of that slot.
4. Rewrite only bullets that materially improve job relevance, requirement coverage, clarity, credibility, or scanability. Recover a fact or stronger framing from the matching canonical block only when it improves the tailored portfolio without losing a stronger current signal.
5. Use only supported terminology. Prefer the job description's exact standard term over a weaker synonym when both have the same substantive meaning, while retaining clear equivalents where useful for human or semantic matching. Leave unsupported requirements as honest gaps.
6. Keep the selected block as a ranked portfolio of distinct evidence. Do not trade away a strong measured achievement merely to insert another keyword, and do not repeat the same requirement across bullets without distinct evidence.
7. In default mode, preserve the rendered footprint using the original rules: retain every edited bullet's rendered line count, or keep its visible-character delta within three when rendering is unavailable.
8. In exact-length mode, preserve each corresponding bullet's exact visible character count. Do not transfer character budget between bullets. Rewrite surrounding supported wording only when needed to fit a useful term naturally at zero character delta.
9. In either mode, leave a bullet unchanged and report the omitted term when it cannot fit truthfully, naturally, and within the active footprint constraint. Never pad with filler or force an awkward synonym merely to satisfy length.
10. Use `apply_patch` to replace only the inner contents of existing `\resumeItem{...}` commands in the selected block of `workspace/tailored.tex`.
11. Preserve bullet count, order, rendered line count, headings, roles, dates, locations, comments, whitespace outside selected bullet bodies, and every unrelated byte.
12. Do not create JSON drafts, preview TeX files, application folders, or a separate approval step.

## Re-audit bold emphasis

Run this pass only after the selected block's visible wording is final.

1. Record the final visible text of every selected bullet, then inspect all existing `\textbf{...}` spans. Do not preserve a span merely because it was previously bold.
2. Judge emphasis against the ranked job requirements and the bullet's actual accomplishment. When company-research mode is active, also use the verified company priorities as secondary context; otherwise use only the job description for company and role relevance.
3. Keep, remove, move, or add `\textbf{...}` so the strongest scan anchors stand out, prioritising:
   - a decision-relevant result, metric, or scale;
   - a differentiating mechanism, architecture, or delivered capability;
   - a supported technology, framework, or method central to a must-have responsibility; and
   - concise external validation when genuinely differentiating.
4. Apply emphasis across the block rather than enforcing one span per bullet. Keep it sparse, vary its placement naturally, and leave a bullet unbolded when it has no decision-relevant anchor. Do not bold action verbs, generic wording, company slogans, whole clauses, or every matching keyword.
5. Treat bolding as a recruiter-scanning aid, not an ATS boost. The underlying supported wording creates keyword coverage; visual emphasis must not override stronger human-readable evidence.
6. During this pass, add or remove only `\textbf{...}` wrappers inside the selected `\resumeItem{...}` bodies. The recorded final visible wording, punctuation, order, and character counts must remain identical.

## Verify and report

- Rerun `python3 scripts/cv_blocks.py list workspace/tailored.tex`, `python3 scripts/cv_blocks.py list workspace/tailored.tex --json`, and `python3 scripts/cv_tex.py workspace/tailored.tex`.
- Confirm `workspace/main.tex` is byte-for-byte unchanged and only the selected tailored bullet bodies changed.
- Verify the active footprint mode:
  - **Default mode:** preserve each edited bullet's rendered line count. Compile and inspect when a LaTeX renderer is available; otherwise require an absolute visible-character delta of at most three and state that line equality is estimated.
  - **Exact-length mode:** compare the selected target's before/after character arrays. Every corresponding delta must be exactly zero; a block average is not sufficient. Also preserve rendered line count when a renderer is available. Without one, report that exact character counts were verified but wrapping remains unverified.
- Confirm every inserted ATS-relevant term is important to the job description, reads naturally, and is supported by current wording, an explicit user fact, or an authorised evidence file.
- Compare before/after requirement coverage and confirm no stronger supported achievement, metric, ownership signal, or technical decision was lost merely to gain keyword coverage.
- Compare every bullet's visible text immediately before and after the emphasis pass; it must be identical. Confirm each remaining bold span is important to the accomplishment and vacancy, not merely an exact keyword match.
- When a renderer is available, confirm the post-emphasis block retains its verified line counts and the CV retains its page count; remove lower-priority emphasis if bold width creates a new wrap. Without a renderer, report post-emphasis wrapping as unverified and direct the user to review it in Overleaf without recommending a LaTeX installation.
- Do not claim guaranteed performance in a company's private ATS.
- Report the target, active footprint and company-research modes, tailored bullets retained, canonical evidence recovered, before/after bullets, exact supported terms added, supported terms omitted because they could not fit naturally, unsupported gaps omitted, requirement-coverage change, per-bullet character deltas, and rendering status. Also list bold spans kept, removed, moved, or added and why the final emphasis is relevant. When research mode was used, cite the official sources and state how they affected prioritisation and emphasis. In exact-length mode, all deltas must be `0`. State that `workspace/tailored.tex` was updated directly and `workspace/main.tex` was not modified.
