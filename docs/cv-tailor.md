# cv-tailor

## Purpose and scope

Tailor selected CV entries or sections to a job description as closely as supported candidate facts allow. Preserve factual accuracy, recruiter readability, technical credibility, and the user's layout.

The `refactor/skill-tailor` branch contains this skill and the supporting components necessary to deliver it, including source parsing, constrained editing, job-description state tracking, and LaTeX compilation and rendered verification. Other skills are outside this branch's scope. Integrate an existing LaTeX compiler; do not build a new typesetting engine.

This document describes agreed behaviour and is updated as decisions evolve. It is not an implementation status report. Technical mechanisms not yet selected are listed separately at the end.

## Inputs and template support

- Require non-empty `workspace/main.tex` and `workspace/job-description.txt`.
- Support Jake's Resume and modified versions whose relevant sections, entries, and bullet commands can be identified reliably.
- Treat `main.tex` as the canonical CV and preserve it during tailoring.
- Candidate facts may come only from `main.tex` and additional information supplied by the user in chat.
- Do not read context folders or supporting documents as candidate evidence for this skill.
- Treat the JD and employer research as information about the vacancy, not evidence of candidate experience.

## Target selection

The user must specify targets before tailoring or researching the vacancy. If scope is absent, ask what to tailor and provide an entry example and a section example:

- “Tailor Wise.”
- “Tailor the Experience section.”

An entry target selects that experience or project only. A section target selects its entries. One request can select multiple entries, multiple sections, or a combination, such as “Tailor Wise and Projects.” Resolve missing or ambiguous targets with the user before editing. Overlapping targets must not cause repeated edits.

If any selected entry contains an empty bullet slot, including mixed filled and empty slots, report the affected entry and direct the user to cv-build. Stop the entire request without editing the destination. Check this before research or preparing edits.

## Source and output behaviour

Write results to `workspace/tailored.tex`.

For every selected target, begin with its original content in `main.tex`, even if that target already has tailored content. Preserve previously tailored content outside selected targets when working against the same JD.

| Situation | Behaviour |
| --- | --- |
| First tailoring request; tailored copy missing or empty | Initialise from `main.tex`, then tailor the selected targets. |
| Same JD; new targets | Use the original selected targets from `main.tex` and replace only those targets in `tailored.tex`. |
| Same JD; repeat target | Tailor the target afresh from `main.tex`, replacing its previous tailored version. |
| Changed JD | Automatically initialise a fresh copy from `main.tex`, tailor the requested targets, and report the reset. Do not ask for reset confirmation. |

The changed-JD reset intentionally replaces previous tailoring throughout the copy. Otherwise, preserve content outside selected targets. Track the normalised JD fingerprint and output-content fingerprint in a versioned LaTeX comment at the start of the private tailored output. Publish this metadata and CV together with one atomic file replacement. Check the JD and existing metadata before other tailoring work. A missing or empty JD, or missing/corrupt/inconsistent metadata on a non-empty existing tailored copy, must be reported before proceeding. Missing metadata is normal when there is no existing tailored output. A valid fingerprint differing from the current JD is a changed-JD reset, not corrupt state. Compare JD text after trimming surrounding whitespace and collapsing consecutive whitespace to one space. Whitespace-only differences preserve existing tailoring; other text changes trigger the reset. Preserve the original JD for interpretation.

## Allowed edits

Normally change only the contents of existing `\resumeItem{...}` commands in selected targets. When a selected entry has a different bullet count in current `main.tex`, synchronise its bullet slots automatically to the canonical count and order before tailoring; do not ask for confirmation. This is an explicit exception to destination bullet-count preservation. Preserve unselected entries. If entry correspondence or a structural replacement cannot be established reliably, report the unsupported structure and leave the destination intact. Preserve bullet count, bullet order, headings, dates, and surrounding source. Never move accomplishments between entries or attribute one role's experience to another.

Within selected bullet bodies, bold emphasis may be added, removed, or moved using `\textbf{...}`. Emphasise important supported accomplishments, results, or relevant technical details sparsely. Measure layout after final emphasis is applied.

## Tailoring and writing rules

- Prioritise relevant accomplishments and experience; use JD terminology where it accurately describes the candidate's work.
- Keep facts clear. Never invent or exaggerate metrics, technologies, scale, responsibility, ownership, outcomes, or causality.
- Keep each bullet focused on one accomplishment using Google's XYZ structure: accomplished X, measured by Y, by doing Z.
- When no numerical measurement is supported, use a supported qualitative result. Do not force a number or claim a result unsupported by evidence.
- Maintain technical credibility for a senior software engineer and clarity for an HR recruiter.
- Avoid keyword stuffing and unnecessary rewriting. A strong, relevant bullet may remain unchanged.
- Let bullets grow or shrink within the rendered constraints below; fixed character counts are not the length requirement.

## Employer research

Research relevant hiring priorities online as part of tailoring. Prioritise the supplied vacancy and current official employer sources. Candidate accounts, Reddit, and similar sources may supplement this research, but must be treated as anecdotal rather than verified hiring policy.

Use research to prioritise supported evidence and emphasis. It must not override explicit JD requirements or create candidate claims. Cite research sources in the final report and distinguish inference from stated employer requirements. Do not publish private CV content or use it in public search queries.

If research is unavailable, continue with the JD and report the limitation. Research depth and recency handling remain implementation decisions.

## Rendered layout requirements

Rendered verification is mandatory. Every edited bullet must occupy at most two rendered lines in the actual CV layout.

### Visual quality

- Prefer one-line bullets that use most of the available width, particularly when neighbouring bullets are also one line.
- Avoid second lines containing only a few overflow words.
- Assess balance across the selected entry. Repeated short second lines create undesirable empty space even when individual bullets satisfy the two-line limit.
- Allow differing line lengths and naturally shorter supporting or final bullets when the entry remains balanced.
- Do not enforce a universal minimum final-line fill percentage: the user's preferred examples include shorter endings.
- Expand only with meaningful, supported information; never add filler to satisfy a visual target.
- Preserve the template's font size, margins, indentation, and spacing. Improve fit through wording.
- Treat character counts as drafting guidance, not proof of rendered fit.

These visual preferences also apply to the future `cv-build` skill; implementing that skill is outside this branch.

### Compilation and verification

Use a local LaTeX compiler to render the complete candidate CV, with its original template settings and dependencies. Match the user's Overleaf compiler, TeX Live version, fonts, and packages as closely as necessary for consistent output. Do not compile isolated bullet snippets with substitute formatting.

Compile all selected changes together per revision round. Measure line count and final-line fullness from the resulting PDF, then inspect rendered entry images for overall balance. Successful compilation alone does not prove that layout passes.

Use a private temporary candidate and outputs. Apply only verified changes to the destination. If compilation or mandatory layout verification cannot be completed, report the blocking issue and leave the existing destination intact, including when a JD reset was planned. Allow at most three failed layout-verification rounds per request, evaluating all selected changes together each round. After the third failure, stop, preserve the destination, and report the remaining issues. The exact validation and write mechanisms remain to be designed.

Compiler installation is a setup dependency. Routine compilation time must be measured against actual templates; do not promise a fixed duration. Reuse an available compiler and keep compilation rounds focused.

## No-change behaviour

If the complete candidate including its JD association equals the existing destination, report unchanged and skip compilation/publication. Restoring canonical wording, synchronising bullet slots, or resetting for a changed JD is an output change and still requires rendered verification.

## Unsupported requirements and final report

Complete supported tailoring even when some JD requirements lack candidate evidence. Report unsupported gaps at the end rather than interrupting to ask about each one. The user may provide additional facts in a follow-up request.

The final report should identify:

- Targets tailored and any targets left unchanged.
- The substantive changes and relevant research sources.
- Rendered verification results and any limitations or failures.
- Unsupported JD requirements.
- Whether a changed JD caused a fresh tailored copy.

Do not claim ATS scores, hiring guarantees, or verified layout when those have not been established.

## Privacy and preservation

Keep CVs, JDs, saved state, compilation outputs, previews, and any backups in ignored private locations. Use synthetic examples in tracked tests and documentation. Preserve unrelated user edits and detect source changes before writing replacements.

## Validation coverage

Verify the observable behaviour with synthetic fixtures:

- Missing inputs and absent or ambiguous targets.
- Entry, section, multiple, and overlapping selections.
- Nested formatting and supported template variations.
- Preservation of bullet count, order, and unrelated bytes.
- Repeated tailoring from original source with other tailored targets preserved.
- Changed-JD reset and failed verification without destination replacement.
- One-, two-, and three-line rendered bullets and short overflow cases.
- Final bold formatting included in layout checks.

Run the repository test suite after script changes. Document supported template conventions and compiler setup for users.

## Decisions to resolve during design

- Supported command and section variations in modified Jake's Resume templates.
- Parser output, target identity, source-change checks, and safe replacement interface.
- Behaviour when main.tex and an existing tailored.tex differ structurally.
- JD-state storage and missing prior JD state.
- Compiler provisioning, environment matching, and PDF-to-bullet mapping.
- Quantitative diagnostics for layout balancing.
- Handling missing supported outcomes or unresolvable template structures.
- Research source selection limits.

## Implementation choices

Generated bullet text is validated for balanced braces, escaped special characters, and an allowlist of formatting commands, then the complete candidate is reparsed. Original unchanged formatting remains supported by the parser. Publication reconstructs the allowed candidate and compares exact bytes before writing.

Rendered verification may use agent-reviewed PDF coordinates and rendered images. Record line count, final-line fullness, mapping confidence, and entry balance against the exact candidate and PDF hashes. Do not claim automated PDF-to-bullet mapping or verified Overleaf equivalence without evidence. Missing rendering or ambiguous mapping blocks publication.
