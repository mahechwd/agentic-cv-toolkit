# LaTeX CV bolding rules

## What to emphasise

- Prefer a metric that communicates outcome or scale. Include its meaningful unit or scale noun when that improves comprehension, such as `\textbf{30\%}`, `\textbf{10M+ organisations}`, or `\textbf{124 ms TTFB / 0.9 s p50}`.
- Bold a differentiating mechanism, architecture, or delivered capability when it carries more signal than a tool name, such as `\textbf{granular, filterable transfers}`, `\textbf{parallelized Camunda workflows}`, or `\textbf{centralized source of truth}`.
- Prefer a technology or method only when it is central to how the result was achieved, such as `\textbf{Kotlin Coroutines}`, `\textbf{Elasticsearch}`, or `\textbf{Azure Kubernetes Service (AKS)}`.
- Use concise external validation, such as an award, only when it is genuinely differentiating and already present in the bullet.
- When a job description is in scope, prioritise supported terms relevant to its must-have work. Relevance never overrides truth.
- Select the shortest phrase that remains meaningful. Keep related adjacent terms in one cohesive span when splitting them would create noisy fragments.

## Distribution across the block

- Do not default to one bold span per bullet. Decide emphasis across the whole selected block.
- Zero to three spans in a bullet is normal. Use a fourth only when every span represents a distinct high-signal category and the result still scans cleanly.
- A metric plus its causal mechanism is a strong two-span pattern. A third central technology or validation signal may be useful when it adds a different kind of evidence.
- Leave bullets unbolded when they contain no decision-relevant anchor. Do not manufacture visual consistency by bolding generic wording.
- Vary the number and placement of spans naturally across bullets. Avoid giving every bullet the same bolding pattern or bolding the first available technology each time.
- Keep bold coverage visually sparse across the block. It should usually occupy less than roughly one-third of a bullet; exceed that only for one cohesive, information-dense phrase that would be less readable if fragmented.

## Restraint

- Leave a bullet unbolded when nothing is sufficiently distinctive.
- Do not bold an entire bullet, full clause, opening action verb, generic soft skill, company name, filler, punctuation, or every technology mentioned.
- Avoid consecutive bold spans that visually merge into a large block.
- Do not nest `\textbf{}` or combine new bolding with italics or underlining.

## Invariants

- Visible wording, punctuation, order, and whitespace-normalised text must remain identical before and after.
- Bold only existing, truthful content; do not introduce a keyword or metric.
- Keep LaTeX escapes inside the bold command.
- Re-render after formatting because bold glyphs can change line wrapping even when visible character count is unchanged.
- Preserve each selected bullet's original rendered line count and the CV's page count. Never leave a bullet above two rendered lines; remove lower-priority emphasis when needed.
- Direct edits may change only existing `\resumeItem{...}` contents in the selected block. Do not create draft or preview files.

## Guidance basis

- MIT career guidance recommends making relevant information immediately visible, quantifying outcomes, and using text emphasis sparingly.
- Oxford career guidance recommends consistent bold text as signposting and warns against overlong, hard-to-scan bullets.
