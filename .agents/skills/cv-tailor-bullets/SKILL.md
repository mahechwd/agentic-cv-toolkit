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
2. Read [../../references/cv-requirement-rules.md](../../references/cv-requirement-rules.md) completely, then read [references/tailoring-rules.md](references/tailoring-rules.md) completely before editing.
3. Run `python3 scripts/cv_blocks.py list workspace/tailored.tex` and require one exact target.
4. Read the whole job description and audit the selected tailored block before consulting its canonical counterpart. Identify achievements already worth retaining, weak or generic wording, missing supported requirements, duplicated signals, and any tailoring that weakened a strong fact.
5. Run `python3 scripts/cv_blocks.py list workspace/main.tex` and inspect only the matching kind and exact target name when it exists. Treat it as a read-only evidence reservoir: identify stronger metrics, technical decisions, ownership, scale, or achievements that are absent or weakened in the tailored block. If no matching canonical target exists, continue from the tailored evidence and report that comparison was unavailable.
6. Use the current tailored target, its matching canonical target, and explicit user facts as the default candidate-evidence set. Never assume canonical wording is stronger or replace the tailored block wholesale.
7. Do not inspect `workspace/context/` unless the user explicitly authorises relevant files or the target folder. A folder request permits non-empty `.md` and `.txt` files only; read a PDF only when the user explicitly names it or asks to read PDFs.
8. Apply the shared role/domain lens, requirement taxonomy, coverage statuses, and placement rules. Never infer candidate experience from the role category.
9. Run `python3 scripts/cv_tex.py workspace/tailored.tex --json` and `python3 scripts/cv_blocks.py list workspace/tailored.tex --json`, then inspect the rest of the tailored CV read-only. Build the shared in-memory coverage ledger and do not create a draft or edit any block other than the selected target.
10. If the user supplies a `$cv-score` scorecard or tailoring handoff for the same job description, use it as advisory input. Revalidate every item against the current job description, exact target list, and authorised candidate evidence; tailoring must not depend on a prior scorecard or trust it blindly.
11. Rank supported ATS-relevant terms by job-description importance and role/domain relevance. Use repetition only to notice omission or noisy overuse; never apply keyword-frequency quotas. Ignore company slogans, generic filler, and unsupported terms.
12. Select company-research mode:
   - **Default:** do not browse for company information.
   - **Research mode:** activate only when the user explicitly asks to research the company or employer. Use current official company sources first—such as the vacancy, careers, product, engineering, security, and about pages—and cite the sources used. If the hiring company cannot be identified confidently, ask rather than researching a similarly named organisation.
   - Use research only to prioritise already-supported achievements and understand product, customer, domain, or engineering concerns. Never use company material as evidence that the candidate has a skill or performed an achievement.
13. Select the footprint mode before editing:
   - **Default mode:** use this unless the user explicitly asks to keep bullet lengths the same.
   - **Exact-length mode:** activate only when the user says, for example, “keep the length the same”, “same character count”, “exact length”, “fixed length”, or “zero delta”. Do not infer this mode merely from a request to preserve layout or keep bullets concise.

## Tailor directly

1. Record the complete canonical CV before editing so any accidental change to it can be detected.
2. Record the selected tailored block's bullet bodies, count, surrounding source, rendered line counts when available, and per-bullet visible character counts from `python3 scripts/cv_blocks.py list workspace/tailored.tex --json`. For every bullet, also record its supported metric or scale, outcome, ownership signal, technical mechanism, domain fact, and differentiating purpose when present.
3. Evaluate each existing tailored bullet against the requirement taxonomy, coverage ledger, role/domain lens, and combined evidence. Apply the change acceptance gate in [references/tailoring-rules.md](references/tailoring-rules.md#change-acceptance-and-stopping-rule) before drafting replacements; retain satisfactory bullets exactly as written.
4. For each proposed wording change, record in memory the current defect, relevant requirement or evidence, and concrete benefit. Prefer the existing wording when alternatives are equally effective; otherwise choose the smallest change that resolves the defect. Recover canonical evidence only when it resolves a recorded gap without losing a stronger current signal.
5. Use only supported terminology. Prefer the job description's exact standard term at a natural, evidenced location when it is more recognisable than a weaker synonym. Retain or pair a clear equivalent, full name, or acronym when that improves human and semantic comprehension without awkward repetition.
6. Do not force a requirement into the selected block merely because it is absent there. If the term is already clearly represented elsewhere in `workspace/tailored.tex`, add it to the selected bullet only when it materially clarifies that specific achievement or proves deeper use.
7. Express behavioural requirements through evidence of action, scope, coordination, or outcome rather than generic adjectives such as “collaborative” or “excellent communicator”. Treat qualifications and certifications as bullet content only when they are genuinely part of the selected achievement.
8. Apply the shared content-strength gate to every inserted term. If it only increases keyword count, omit it.
9. Keep the selected block as a ranked portfolio of distinct evidence. Do not trade away a strong measured achievement merely to insert another keyword, and do not repeat the same requirement across bullets without distinct evidence.
10. Compare every proposed bullet with its recorded signals. Reject a rewrite that loses a supported metric, scale, outcome, ownership signal, mechanism, domain fact, or differentiating purpose merely to gain terminology. Allow a deliberate trade only when it produces a clearly stronger truthful accomplishment for a higher-priority requirement, and report the trade.
11. In default mode, preserve the rendered footprint using the original rules: retain every edited bullet's rendered line count, or keep its visible-character delta within three when rendering is unavailable.
12. In exact-length mode, preserve each corresponding bullet's exact visible character count. Do not transfer character budget between bullets. Rewrite surrounding supported wording only when needed to fit a useful term naturally at zero character delta.
13. In either mode, leave a bullet unchanged and report the omitted term when it cannot fit truthfully, naturally, and within the active footprint constraint. Never pad with filler or force an awkward synonym merely to satisfy length.
14. Use `apply_patch` only for replacements that pass the change acceptance gate, replacing only the inner contents of existing `\resumeItem{...}` commands in the selected block of `workspace/tailored.tex`. Leave every other bullet body byte-for-byte unchanged.
15. Preserve bullet count, order, rendered line count, headings, roles, dates, locations, comments, whitespace outside selected bullet bodies, and every unrelated byte.
16. Do not create JSON drafts, preview TeX files, application folders, or a separate approval step.

## Re-audit bold emphasis

Run this pass only after the selected block's visible wording is final.

1. Record the final visible text of every selected bullet, then inspect all existing `\textbf{...}` spans. Apply the same change acceptance gate to emphasis: retain suitable spans exactly, and record a specific scanning or relevance defect before changing a span.
2. Compare candidate spans using the emphasis selection guidance in [references/tailoring-rules.md](references/tailoring-rules.md): hiring value, relevance to must-have or core responsibilities, specificity, and usefulness during a quick scan. Use these as judgement criteria, not a numeric score. When company-research mode is active, use verified company priorities as secondary context; otherwise use only the job description for company and role relevance.
3. Keep, remove, move, or add `\textbf{...}` to expose the strongest evidence: meaningful results or scale, differentiating mechanisms or delivered capabilities, central supported technologies, or concise external validation. Prefer the more JD-relevant span when candidates offer comparable hiring value; preserve exceptional transferable evidence even when the JD does not name it.
4. Review emphasis across the block. Usually zero to two short spans per bullet are enough, but this is a guide, not a quota or hard cap. Add another only when it exposes distinct, important evidence without making the bullet visually busy. Leave bullets unbolded when no anchor merits emphasis. Avoid adjacent fragmented highlights, repeated low-value technology highlights, and bolding most of a sentence. Do not bold action verbs, generic wording, company slogans, whole clauses, or every matching keyword.
5. Treat bolding as a recruiter-scanning aid, not an ATS boost. The underlying supported wording creates keyword coverage; visual emphasis must not override stronger human-readable evidence.
6. During this pass, add or remove only `\textbf{...}` wrappers inside the selected `\resumeItem{...}` bodies. The recorded final visible wording, punctuation, order, and character counts must remain identical.

If no wording or emphasis change passes the gate, finish the audit without patching the selected block. A repeated tailoring request does not itself justify another rewrite.

## Verify and report

- Rerun `python3 scripts/cv_blocks.py list workspace/tailored.tex`, `python3 scripts/cv_blocks.py list workspace/tailored.tex --json`, and `python3 scripts/cv_tex.py workspace/tailored.tex`.
- Confirm `workspace/main.tex` is byte-for-byte unchanged and only the selected tailored bullet bodies changed.
- Verify that every final wording or emphasis change resolves its recorded defect and delivers the stated benefit. Reject changes supported only by a preference between equally effective variants; retain the original body or span. Do not calculate a score to justify an edit.
- Verify the active footprint mode:
  - **Default mode:** preserve each edited bullet's rendered line count. Compile and inspect when a LaTeX renderer is available; otherwise require an absolute visible-character delta of at most three and state that line equality is estimated.
  - **Exact-length mode:** compare the selected target's before/after character arrays. Every corresponding delta must be exactly zero; a block average is not sufficient. Also preserve rendered line count when a renderer is available. Without one, report that exact character counts were verified but wrapping remains unverified.
- Confirm every inserted ATS-relevant term is important to the job description, reads naturally, and is supported by current wording, an explicit user fact, or an authorised evidence file.
- Recheck the coverage ledger after editing. Confirm exact and equivalent coverage was recorded by location, no unrelated block was changed, and no term was duplicated in the selected block solely to increase frequency.
- Confirm every new term passes the content-strength gate and that behavioural requirements are demonstrated rather than asserted.
- Compare before/after requirement coverage and the recorded per-bullet signals. Confirm no stronger supported metric, scale, outcome, ownership signal, mechanism, domain fact, or differentiation was lost merely to gain keyword coverage.
- Compare every bullet's visible text immediately before and after the emphasis pass; it must be identical. Confirm each remaining bold span exposes important evidence for the vacancy or exceptional transferable value. Read the highlighted phrases across the block as a quick scan: they should reveal distinct accomplishments or capabilities, not just a repeated tool list. Remove emphasis that adds visual noise without helping that scan.
- When a renderer is available, confirm the post-emphasis block retains its verified line counts and the CV retains its page count; remove lower-priority emphasis if bold width creates a new wrap. Without a renderer, report post-emphasis wrapping as unverified and direct the user to review it in Overleaf without recommending a LaTeX installation.
- Do not claim guaranteed performance in a company's private ATS.
- Report the target, role/domain lens, active footprint and company-research modes, any supplied handoff items addressed or rejected, tailored bullets retained, canonical evidence recovered, before/after bullets, exact terms added, equivalent or existing coverage retained elsewhere, supported terms omitted because they could not fit naturally, unsupported gaps omitted, requirement-coverage change, content-signal preservation or deliberate trade, per-bullet character deltas, and rendering status. For each changed bullet or bold span, state the concrete defect resolved and the benefit; summarise satisfactory retained content without inventing improvement claims. When research mode was used, cite the official sources and state how they affected prioritisation and emphasis. In exact-length mode, all deltas must be `0`. State whether the selected block was updated or left unchanged, and that formal rescoring remains the responsibility of `$cv-score`. When no edit passes the gate, use a concise unchanged report with the target, audit result, unresolved gaps or constraints, and verification status instead of a fabricated before/after rewrite.
