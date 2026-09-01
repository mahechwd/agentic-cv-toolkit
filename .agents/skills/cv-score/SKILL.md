---
name: cv-score
description: Score a LaTeX CV against a pasted job description using fixed ATS-readiness and hiring-manager rubrics out of 100, then identify supported missing keywords, unsupported gaps, strengths, red flags, weak sections, and interview likelihood. Use for evaluation before or after tailoring. Do not edit the CV or pretend to reproduce a company's private ATS.
---

# CV score

Produce a candid, repeatable job-fit assessment without modifying any files.

## Select inputs

- If the user names a CV path, use that exact path and do not apply an automatic fallback.
- If the user does not name a CV path, inspect the files without modifying them:
  1. Use `workspace/tailored.tex` when it exists and contains non-whitespace content.
  2. Otherwise fall back to `workspace/main.tex`.
  3. Stop and report the missing input if the selected fallback is also missing or empty.
- State which CV path was selected. When automatic fallback occurs, state that `workspace/tailored.tex` was empty or missing and `workspace/main.tex` was used instead.
- Use the non-empty `workspace/job-description.txt` with either CV. Stop if the vacancy is empty or still contains placeholder text.
- Read [../../references/cv-requirement-rules.md](../../references/cv-requirement-rules.md) completely, then read [references/scoring-rubric.md](references/scoring-rubric.md) completely before scoring.
- Run `python3 scripts/cv_tex.py <cv-path> --json` so LaTeX commands do not distort semantic review or visible character counts.
- Run `python3 scripts/cv_blocks.py list <cv-path> --json` so every handoff recommendation uses an exact experience or project target name.

## Analyse the job and CV

1. Build the shared requirement taxonomy, role/domain lens, and coverage ledger from `cv-requirement-rules.md`.
2. Consult `workspace/context/` only when the user explicitly authorises relevant files or a target folder; otherwise use only the CV and explicit prompt facts as candidate evidence.
3. Score every rubric component independently and cite concise CV/job evidence for each deduction.
4. For each supported missing or underrepresented requirement, identify the strongest truthful placement. Prefer an exact experience or project target from `cv_blocks.py`; when another section would be better, label it as an out-of-scope placement rather than inventing a target.
5. When a prior scorecard for the same job description is supplied, apply the frozen comparison rules. Show category and requirement-status deltas and identify which content changes produced them.
6. When the prior CV or its before-bullets are available, run a regression check for lost metrics, scale, ownership, mechanisms, outcomes, domain clarity, and differentiating evidence. Reflect genuine losses in the relevant rubric component without double-deducting the same weakness.

## Optional rendered parsing check

- Run this check only when the user explicitly asks for a rendered ATS or PDF parsing check, asks to inspect PDFs, or names the exact PDF. Do not open an existing PDF merely because it is present.
- If an exact PDF is authorised, extract its text and compare the reading order with the source CV. Otherwise, when a LaTeX renderer and a PDF text extractor are already available, compile the selected CV into an operating-system temporary directory and inspect that generated PDF there.
- Never install or recommend a LaTeX distribution or PDF extractor solely for scoring. If the tools are unavailable, continue with source-level analysis and lower the parseability confidence.
- Check that contact information, conventional section headings, employers or projects, dates, and bullet text are extractable and appear in a sensible order. Report missing, corrupted, duplicated, or reordered text separately from semantic job fit.
- Do not write generated PDFs, extracted text, or parsing reports into the repository.

## Output

Present:

- **ATS Readiness Score:** integer out of 100, component breakdown, and confidence.
- **Hiring Manager Score:** integer out of 100, component breakdown, and confidence.
- **Supported Missing or Underrepresented Keywords:** up to 20, ranked by job importance, with the evidence that permits each one.
- **Unsupported Gaps:** important job requirements that must not be inserted as claims.
- **Red Flags:** the three most consequential issues visible in a rapid scan.
- **Biggest Strengths:** the three strongest reasons to interview.
- **Weak Sections:** vague, repetitive, low-value, poorly placed, or space-wasting content.
- **Interview Likelihood:** a reasoned range and low/medium/high label, with assumptions and confidence.
- **Priority Improvements:** the smallest truthful changes most likely to improve the result.
- **Tailoring Handoff:** a ranked set of concrete, read-only actions. For each action include the requirement, status, evidence, preferred exact phrase or equivalent, recommended CV path and exact kind/name/bullet when applicable, priority, and rubric component affected.
- **Regression Check:** on a comparable rescore, list preserved gains and any lost metrics, impact, ownership, technical depth, or differentiation.
- **Rendered Parsing Check:** pass/fail/not-run, evidence inspected, issues, and confidence.

State the CV path scored and whether a frozen baseline was used. State that both scores and interview likelihood are heuristic estimates, not outputs from the employer's actual ATS or recruiting process. Do not edit the CV while scoring or persist a handoff file.
