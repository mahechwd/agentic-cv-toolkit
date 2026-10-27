---
name: cv-tailor
description: Tailor selected entries or sections of a Jake-style LaTeX CV to workspace/job-description.txt, preserving canonical facts and publishing workspace/tailored.tex only after rendered layout review. Use for job-specific CV tailoring, including multiple targets; not for filling empty bullet slots or scoring a CV.
---

# CV tailoring

Use this repository's helpers from its root (three directories above this file). Read [the operating procedure](references/workflow.md) before executing. The behaviour contract is [docs/cv-tailor.md](../../../docs/cv-tailor.md).

## Inputs and scope

Check the JD and existing output state first with `scripts/cv_tailor.py check`. Missing/empty JD or missing/inconsistent metadata on an existing non-empty tailored copy must be reported before other work. Never silently adopt an unknown copy or rewrite its metadata. Do not run setup_workspace.py: it deletes private inputs.

Require selected targets before research or tailoring. If absent, ask what to tailor, offering both “Tailor Wise” and “Tailor the Experience section.” Accept entries, sections, or combinations. Resolve names using the parser and confirm genuinely ambiguous selections. Overlaps are deduplicated. Any selected empty bullet stops the whole request; direct the user to build those bullets first.

Candidate facts come only from current `workspace/main.tex` and explicit user facts in chat. Do not open context folders or supporting documents. Use the JD and employer research only to prioritise supported experience. Never transfer accomplishments between entries or invent outcomes, ownership, technologies, measurements, or causality.

## Writing decisions

Start each selected target afresh from canonical wording, even on repeat requests. Keep current canonical bullet count and order, including newly added bullets. For the same JD preserve unselected tailoring. A changed JD automatically stages a fresh canonical copy; report the reset only if published. Normalised whitespace-only JD changes do not reset.

Read the full original JD. In memory, distinguish essential requirements, preferred skills, responsibilities, and domain signals. Map each to supported canonical evidence or an unsupported gap. Read other CV entries for placement and redundancy, but change only selected entries. Do not use keyword quotas or promise ATS scores.

Use XYZ-style accomplishments: what was delivered, a supported quantitative or qualitative result, and one meaningful technical method. Preserve strong wording when no useful improvement is supported. Make the opening understandable to a recruiter and the method credible to a senior engineer. Never invent a result merely to complete the formula. Keep one main accomplishment per bullet.

Research the vacancy and relevant employer priorities using current official sources first. Search using employer, role, and public vacancy terms only; never private CV text. Check relevance and dates. Anecdotal sources may supplement, but distinguish them from official requirements. Stop when research adds no useful prioritisation. If unavailable, continue with the supplied JD and disclose that limitation. Cite sources used in the final report.

Apply sparse `\textbf{...}` emphasis after wording is settled. Prefer important outcomes, mechanisms, or relevant supported technical details. Bolding is for scanning, not an ATS claim.

## Verification and delivery

Use the helper to stage all selected changes together in a private temporary session. Never directly overwrite tailored.tex. Validate authored LaTeX and reparse the complete candidate. Compile using the original template settings and dependencies, then measure and visually inspect every selected bullet after final bolding.

Each edited bullet must fit at most two rendered lines. Avoid repeated sparse second lines; prefer reasonably full one-line bullets. Assess entry balance without a universal minimum fill percentage. Improve wording, never font size, margins, spacing, or unsupported filler.

An identical complete destination needs no compilation or write. Canonical restoration, bullet-count synchronisation, or a JD reset is a real output change and requires review. Use the same session for revisions. Record every failed layout review; after three failures stop with the existing destination intact. Missing compiler, failed compilation, uncertain mapping, or changed source also blocks publication.

The review is performed by you using actual coordinates and images, not by the user as a separate approval step. Never fabricate a passing receipt. Publish only the exact reviewed candidate through the helper.

Report targets changed/unchanged, substantive changes, cited research, rendered results and limitations, unsupported JD gaps, and whether a changed JD reset was published. Do not claim Overleaf equivalence unless the environment has been checked. Keep all private artifacts out of tracked files.
