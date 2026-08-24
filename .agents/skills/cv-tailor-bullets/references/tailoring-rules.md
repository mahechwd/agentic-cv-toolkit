# Job-description tailoring rules

## Truth before keyword coverage

- Never add a technology, method, responsibility, ownership level, metric, or domain claim merely because it appears in the job description.
- Insert a keyword only when the selected bullet, an explicit user fact, or authorised evidence supports the same substantive meaning.
- Equivalent terminology may be substituted when accurate, such as expanding an evidenced abbreviation to the job description's full phrase.
- Treat unsupported requirements as gaps to report, not prose to manufacture.

## ATS-oriented term selection

- Treat the job description as a source of matching vocabulary, never as evidence about the candidate.
- Extract exact phrases from required qualifications, core responsibilities, named technologies or practices, and precise domain terminology.
- Rank terms by requirement strength, meaningful repetition, relevance to the selected target, and whether the candidate's evidence supports the exact substantive claim.
- Prefer the employer's exact standard term over a weaker synonym when both mean the same thing and the result remains natural and accurate.
- Place each term in the bullet whose evidence proves it. Do not distribute isolated keywords across unrelated bullets.
- Ignore company slogans, generic personality adjectives, boilerplate benefits language, and repetition that adds no information.
- Optimise for truthful keyword recognition and human readability; never promise a score, ranking, interview, or successful match in a company's private ATS.

## Natural relevance

- Prioritise must-have requirements and core responsibilities over incidental repeated words.
- Use a job-description phrase only when it makes the bullet more precise or recognisable.
- Preserve the achievement and technical causal chain; do not turn bullets into keyword lists.
- Prefer concrete nouns and industry-standard terms to vague synonyms.
- Retain strong differentiating evidence even when the vacancy does not repeat it.
- Avoid copying long phrases or company marketing language verbatim.

## Bullet quality and footprint

- Start with an accurate action verb and keep each bullet focused on one primary achievement.
- State the result or contribution, supported measurement when available, and technical mechanism in a natural order.
- Preserve British English, truth-preserving qualifiers, and concise sentence fragments.
- Preserve the rendered line count of every edited bullet.
- In default mode, use actual rendering when available. Without a renderer, keep every corresponding bullet within three visible characters of its original length and state that line equality is estimated.
- Activate exact-length mode only when the user explicitly requests the same, exact, or fixed length or character count. In this mode, every corresponding bullet must have a visible-character delta of `0`; a block average or shared allowance is not sufficient.
- For exact-length mode, measure visible text using the selected target's `characters` values from `python3 scripts/cv_blocks.py list workspace/tailored.tex --json`; do not count LaTeX command syntax as visible wording or move unused character budget between bullets.
- Character equality is not proof of layout equality because bold text, punctuation, and wide glyphs affect proportional-font width. Verify actual wrapping when a renderer is already available; otherwise state the applicable limitation.
- Rewrite surrounding supported prose only when it keeps the claim accurate and natural. Do not add filler, redundant modifiers, or awkward synonyms to meet either footprint constraint.
- When keyword insertion conflicts with truth, readability, the active length constraint, or layout, leave that bullet unchanged and report the omitted term.

## Scope and LaTeX

- Edit only the selected block in `workspace/tailored.tex`; never edit `workspace/main.tex`.
- Preserve active bullet count, order, and all content outside selected `\resumeItem{...}` bodies.
- Escape literal LaTeX-sensitive characters.
- Do not add bold formatting during tailoring; use `$cv-bold-highlights` separately on `workspace/tailored.tex` when requested.
