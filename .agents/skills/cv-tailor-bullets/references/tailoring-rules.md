# Job-description tailoring rules

## Truth before keyword coverage

- Never add a technology, method, responsibility, ownership level, metric, or domain claim merely because it appears in the job description.
- Insert a keyword only when the selected bullet, an explicit user fact, or authorised evidence supports the same substantive meaning.
- Equivalent terminology may be substituted when accurate, such as expanding an evidenced abbreviation to the job description's full phrase.
- Treat unsupported requirements as gaps to report, not prose to manufacture.

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
- Aim for no more than a three-visible-character difference from the corresponding source bullet until actual rendering is available.
- Character equality is not proof of layout equality because bold text, punctuation, and wide glyphs affect proportional-font width.
- When keyword insertion conflicts with truth or layout, retain the stronger truthful bullet and report the omitted term.

## Scope and LaTeX

- Edit only the selected block in `workspace/tailored.tex`; never edit `workspace/main.tex`.
- Preserve active bullet count, order, and all content outside selected `\resumeItem{...}` bodies.
- Escape literal LaTeX-sensitive characters.
- Do not add bold formatting during tailoring; use `$cv-bold-highlights` separately on `workspace/tailored.tex` when requested.
