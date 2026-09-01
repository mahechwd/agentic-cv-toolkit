# Shared CV requirement rules

`$cv-score` and `$cv-tailor-bullets` must use these definitions so analysis, editing, and rescoring do not drift.

## Requirement priority and categories

Classify vacancy requirements by both priority and category.

- **Must-have:** explicitly required, essential, or central to eligibility.
- **Core responsibility:** work the successful candidate is expected to perform regularly.
- **Preferred:** useful but not required.
- **Incidental:** repeated or visible wording that does not materially define candidate fit.

Use these categories:

- hard skills, technologies, platforms, and tools;
- methodologies, architecture, and engineering practices;
- responsibilities and behavioural signals;
- industry and domain terminology; and
- qualifications or certifications.

Do not rank raw repetition above explicit requirement strength, responsibility prominence, or semantic importance.

## Coverage statuses

- **Exact:** the job description's term appears naturally in the CV with truthful context.
- **Equivalent:** an unambiguous substantive equivalent or common variation appears; do not penalise harmless wording differences.
- **Supported but absent:** candidate evidence supports the requirement, but neither the exact term nor a clear equivalent appears.
- **Supported but underrepresented:** strong evidence exists, but the requirement is weakly expressed, vague, or poorly placed relative to its importance.
- **Unsupported:** no authorised candidate evidence supports the claim.

A Skills-section term counts as textual coverage but does not prove applied experience. Employer requirements, company research, and the job description never count as candidate evidence.

## Coverage ledger

Maintain the ledger in memory; never create a draft file solely for it. For each material requirement record:

- priority and category;
- exact job-description phrase;
- truthful equivalent or variation;
- current path, section, and exact experience or project target where applicable;
- authorised candidate evidence;
- coverage status; and
- recommended action or reason for no action.

Use `python3 scripts/cv_blocks.py list <cv-path> --json` for exact target names and `python3 scripts/cv_tex.py <cv-path> --json` for visible bullet text. Inspect frequency only to detect omission, duplication, or stuffing. Never require fixed repetitions or a universal match percentage.

## Placement and content strength

- Prefer one natural, evidenced use of an exact employer term to repeated low-information mentions.
- Preserve an expanded name, common acronym, or clear equivalent when it improves human and semantic comprehension.
- Recommend the location whose evidence best proves the requirement. Do not insert a term into an unrelated achievement merely because that block has space.
- Demonstrate behavioural requirements through action, scope, coordination, or outcome rather than generic labels.
- A proposed term must clarify what was delivered, how it was achieved, why it mattered, the candidate's ownership, or the relevant domain. If it only raises keyword count, reject it.
- Unsupported requirements remain gaps. Never invent a skill, metric, scale, title, certification, responsibility, outcome, or causal relationship.

## Role-specific evidence priorities

Infer the role family and domain from the job description, then prioritise supported evidence accordingly:

- **Backend:** APIs, data modelling, distributed systems, correctness, reliability, latency, and throughput.
- **Frontend:** user experience, accessibility, state management, performance, design-system quality, and measurable adoption.
- **Full-stack or product engineering:** shipped user value, end-to-end ownership, experimentation, integration, and delivery.
- **Platform or infrastructure:** automation, deployment, observability, scalability, resilience, developer experience, and cost.
- **Security:** vulnerabilities, threat reduction, controls, secure design, detection, incident response, and risk.
- **Data or machine learning:** data quality, pipelines, evaluation, model or inference performance, reproducibility, and monitoring.
- **Mobile or embedded:** resource constraints, reliability, device integration, responsiveness, and release quality.
- **Quantitative or financial engineering:** modelling, correctness, latency, risk, auditability, and supported financial impact.

These are prioritisation lenses, not mandatory keyword lists. Retain exceptional transferable evidence of impact, ownership, scale, or engineering judgement.

## Frozen before-and-after comparison

When rescoring the same CV against the same job description with a supplied baseline scorecard:

- freeze the requirement set, priority, category, rubric weights, and interpretation of substantive equivalents;
- freeze the authorised evidence basis unless the user supplies new evidence;
- compare coverage status, location, rubric components, strengths, gaps, and regressions against that baseline;
- disclose any necessary interpretation change and restate the affected baseline rather than silently moving the standard; and
- never credit repetition without stronger evidence.

If the job description or scoring rubric changed, treat the result as a new assessment rather than a comparable delta.
