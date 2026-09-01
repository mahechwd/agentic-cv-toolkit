# Job-description tailoring rules

## Evidence hierarchy and cross-file comparison

- Audit the selected block in `workspace/tailored.tex` first. Preserve tailored wording that already communicates the strongest truthful and relevant achievement.
- Then compare only the matching kind and exact target in `workspace/main.tex`. Use canonical bullets as additional candidate evidence, not as the preferred answer and never as permission to reset or overwrite tailored work wholesale.
- Recover canonical metrics, mechanisms, scope, ownership, or achievements only when they strengthen job alignment or restore evidence weakened by earlier tailoring.
- When the two files describe the same achievement differently, retain the strongest supported combination of impact, clarity, technical credibility, and job relevance. Do not merge incompatible causal claims.
- Candidate evidence comes from the current tailored block, the matching canonical block, explicit user facts, and explicitly authorised context. The job description and company research describe employer needs; they never prove candidate experience.

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

## Shared requirement decisions

- Apply the taxonomy, coverage statuses, ledger, placement rules, content-strength gate, role priorities, and frozen-comparison definitions from `../../../references/cv-requirement-rules.md`.
- Keep the ledger in memory and inspect the wider tailored CV read-only. Edit only the selected exact target even when another placement would be stronger; report that opportunity instead.
- A supplied scorecard or tailoring handoff is advisory. Revalidate it against the current files and evidence, and reject any item that is stale, unsupported, poorly placed, or weaker than the current achievement.
- Do not calculate a score inside the tailoring skill. Leave comparable rescoring to `$cv-score`.

## Optional company research

- Research the hiring company only when the user explicitly requests it. Ordinary tailoring relies on the supplied job description.
- Prefer current first-party sources: the official vacancy, careers pages, product documentation or pages, engineering or security material, and the company's about page.
- Extract only decision-useful context such as products, customers, domain vocabulary, engineering priorities, reliability or security concerns, and stated role expectations.
- Use that context to rank already-supported candidate achievements and choose accurate vocabulary. Do not add company praise, marketing slogans, speculative strategy, or claims that the candidate worked at the company's scale.
- Keep the job description primary for ATS terminology. Company research is secondary and should improve role context and hiring-manager relevance rather than displace explicit vacancy requirements.
- Cite sources used and distinguish sourced facts from tailoring inferences.

## Natural relevance

- Prioritise must-have requirements and core responsibilities over incidental repeated words.
- Use a job-description phrase only when it makes the bullet more precise or recognisable.
- Preserve the achievement and technical causal chain; do not turn bullets into keyword lists.
- Prefer concrete nouns and industry-standard terms to vague synonyms.
- Retain strong differentiating evidence even when the vacancy does not repeat it.
- Treat the selected block as a portfolio: retain distinct high-signal evidence instead of spending every bullet on the same keyword or requirement.
- A newly inserted term must strengthen the achievement by clarifying what was delivered, how it was achieved, why it mattered, the candidate's ownership, or the relevant domain. Omit it when it only raises a keyword count.
- Do not repeat a term in the selected target merely because it is absent from that block when the wider tailored CV already provides clear, appropriately placed coverage.
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

## Post-tailoring emphasis

- Finalise visible wording before revisiting bold emphasis. Use the post-rewrite wording as an immutable baseline for the emphasis pass.
- Reassess every existing bold span; earlier emphasis may no longer match the tailored achievement or vacancy.
- Prioritise meaningful outcomes or scale, differentiating mechanisms or capabilities, and central supported technologies that align with important job requirements. Company research may influence this ranking only when research mode was explicitly activated.
- Keep emphasis sparse across the block. Do not enforce one span per bullet, and allow unbolded bullets when no anchor deserves emphasis.
- Prefer the shortest cohesive span that remains meaningful. A metric plus its causal mechanism can form two useful anchors when both are independently important.
- Do not bold opening verbs, generic soft skills, company names, marketing language, full clauses, every technology, or a keyword solely because it appears in the job description.
- Bolding is for human scanning and does not create ATS evidence or permission to add a claim.
- Add or remove only `\textbf{...}` wrappers during the emphasis pass. Visible wording, punctuation, order, whitespace-normalised text, and visible character counts must remain unchanged.
- Bold glyphs can alter wrapping. Preserve line and page counts when rendering is available by removing lower-priority emphasis; otherwise report wrapping as unverified and let the user review it in Overleaf.

## Scope and LaTeX

- Edit only the selected block in `workspace/tailored.tex`; never edit `workspace/main.tex`.
- Preserve active bullet count, order, and all content outside selected `\resumeItem{...}` bodies.
- Escape literal LaTeX-sensitive characters.
- The post-tailoring emphasis pass may change only `\textbf{...}` wrappers after visible wording is final. `$cv-bold-highlights` remains available for standalone bold-only requests.
