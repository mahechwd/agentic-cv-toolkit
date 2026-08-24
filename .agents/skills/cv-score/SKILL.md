---
name: cv-score
description: Score a LaTeX CV against a pasted job description using fixed ATS-readiness and hiring-manager rubrics out of 100, then identify supported missing keywords, unsupported gaps, strengths, red flags, weak sections, and interview likelihood. Use for evaluation before or after tailoring. Do not edit the CV or pretend to reproduce a company's private ATS.
---

# CV score

Produce a candid, repeatable job-fit assessment without modifying any files.

## Select inputs

- Use the CV path named by the user. Otherwise use canonical `workspace/main.tex` for a baseline score; use `workspace/tailored.tex` when the user asks to score the tailored CV.
- Use the non-empty `workspace/job-description.txt` with either CV. Stop if the vacancy is empty or still contains placeholder text.
- Read [references/scoring-rubric.md](references/scoring-rubric.md) completely before scoring.
- Run `python3 scripts/cv_tex.py <cv-path> --json` so LaTeX commands do not distort semantic review or visible character counts.

## Analyse the job and CV

1. Separate must-have qualifications, preferred qualifications, responsibilities, technologies, domain language, and behavioural expectations.
2. Distinguish exact terms from substantive equivalents; do not penalise harmless wording differences.
3. Classify important terms as present, supported but absent, supported but underrepresented, or unsupported. Consult `workspace/context/` only when the user explicitly authorises relevant files or a target folder; otherwise use only the CV and explicit prompt facts.
4. Score every rubric component independently and cite concise CV/job evidence for each deduction.
5. Use the same rubric and interpretation when rescoring a tailored CV. If a prior scorecard is supplied, show category deltas rather than silently changing standards.

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

State that both scores and interview likelihood are heuristic estimates, not outputs from the employer's actual ATS or recruiting process. Do not edit the CV while scoring.
