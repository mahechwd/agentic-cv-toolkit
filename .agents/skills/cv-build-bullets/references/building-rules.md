# Content-first CV bullet rules

## Evidence and integrity

- Use only facts supported by pasted or current bullet wording, facts explicitly supplied by the user, or context sources the user explicitly authorised the skill to read.
- Treat optional context as corroboration or additional evidence, not as a mandatory input.
- Never invent or strengthen metrics, scale, ownership, technologies, outcomes, or business impact.
- Omit unsupported metrics; never insert placeholders such as `[X%]`.
- Resolve material conflicts before editing.
- Exclude credentials, personal information, internal identifiers, and confidential implementation details unsuitable for a public CV.

## Curate a portfolio of signals

- Build the block as a ranked portfolio, not a chronological task list or an inventory of everything implemented.
- Rank candidate achievements by external or user value, supported measurement or scale, personal ownership, engineering judgement, relevance, and how much new information they add to the block.
- When evidence permits, use the opening bullet to establish the product, platform, system, ownership, or scale. Use later bullets for distinct performance, reliability, security, architecture, delivery, adoption, or operational signals.
- A short final bullet can add valuable breadth through deployment, production debugging, observability, testing, or incident work. Keep it short when the complete claim is short; do not inflate it into another flagship bullet.
- Do not repeat the same system description in every bullet. After the block establishes context, spend later words on a new outcome or engineering decision.
- If there are more strong achievements than existing slots, keep the highest-signal claims and report the strongest omission. Do not merge several achievements or preserve low-level detail merely to avoid leaving evidence unused.
- If the evidence supports only one narrow project, vary the signal within that truthful scope rather than inventing breadth.

## Recruiter-readable technical credibility

- Start with an accurate action verb and use concise British English.
- Lead with the plain-English accomplishment, user or business value, or measurable engineering result. Put implementation detail after the reader understands why the work mattered.
- Make the opening clause understandable to a general recruiter without requiring them to decode the technology stack, architecture, or internal system vocabulary.
- Make the subject of the opening clause the system, capability, user outcome, scale, or measurable change—not a chain of tools or internal workflow states.
- Make the XYZ relationship explicit: state the accomplishment (X), include its measurement or scale (Y) when supported, and explain the technical method (Z).
- Prefer compact causal forms such as “Reduced X by Y by implementing Z” or “Built Z, enabling X at Y scale”. Do not force a metric or awkward sentence order when the evidence lacks Y.
- Lead with the most differentiating result or engineering contribution rather than a duty.
- Name only the one or two technologies, frameworks, algorithms, or architectural choices that best explain how the result was achieved. Do not turn a bullet into a stack inventory.
- Choose the smallest concrete technical detail that proves engineering credibility, such as a design decision, constraint, algorithm, scale characteristic, or reliability mechanism. Do not preserve every available implementation detail.
- Demonstrate senior-level depth through causality and judgement—why the method produced the result or handled a constraint—not through dense terminology.
- Replace internal names and niche jargon with their plain-English function. Use an acronym without expansion only when it is broadly recognised for the target role and genuinely improves the bullet.
- Treat technologies as evidence for the claim, not the claim itself. Prefer recognisable platform, framework, or architecture signals over low-level query names, labels, workflow states, or multiple threat-data acronyms.
- When a bullet contains several niche acronyms or internal terms, keep only the one that most strengthens credibility and translate or remove the rest. A recruiter should not need a lookup to understand the result.
- Phrase user-facing work around enablement or adoption when supported, such as what teams could do, rather than leading with a UI action such as “displayed”.
- When no percentage or latency metric exists, use a concrete evidenced effect—eliminated redundant work, prevented incorrect results, enabled self-service, preserved compatibility—rather than a vague claim such as “improved scalability”.
- Avoid long chains of technical nouns, multiple parenthetical explanations, and lists of tools joined by commas.
- Give every bullet a distinct purpose and avoid repeated opening verbs, claims, metrics, and tool lists.
- Prefer clear technical language to grandiose or unusual verbs. Avoid first-person pronouns, vague praise, filler, keyword stuffing, and unverifiable adjectives such as “top 5%”.
- Metrics may quantify performance, scale, reliability, coverage, latency, cost, adoption, delivery, or accuracy. A bullet remains valid without a metric when its technical contribution is strong and evidence-backed.
- Give each bullet one main accomplishment and one causal chain. Do not combine two independently valuable achievements merely because they came from the same source sentence.
- Split separate achievements across available bullet slots when each has its own outcome, method, or evidence. Avoid joining them with “and” unless the second phrase directly completes the same mechanism or result.

## Two-audience test

- **HR scan:** after reading the opening clause, a non-technical recruiter can state what improved, what was delivered, or why the work mattered.
- **Senior SWE scan:** after reading the full bullet, an experienced engineer can identify a concrete method, engineering decision, constraint, or scale signal that makes the claim credible.
- If only the HR test passes, add one supported technical mechanism. If only the senior SWE test passes, simplify the opening and remove low-signal implementation detail.
- Prefer “Improved payment retrieval speed by 30% by redesigning Elasticsearch pagination” to a catalogue of service types, indexing internals, infrastructure, and query primitives.
- **Six-second block scan:** reading only the opening clause of each bullet should reveal several distinct reasons to interview the candidate. If every opening sounds like another implementation step in the same pipeline, re-rank the evidence and rewrite around outcomes.

## Length and focus

- Use a hard ceiling of 220 visible characters per bullet, including spaces and punctuation, unless the user explicitly supplies a different limit.
- Enforce 180 visible characters as the default maximum block average in CV edit mode. It is a ceiling, not a target; there is no minimum or preferred lower bound.
- Keep a strong bullet shorter when the complete supported XYZ claim needs fewer words. Never pad with extra technologies, adjectives, or context merely to make it longer.
- Allow flagship and supporting bullets to have naturally different lengths. Do not homogenise the block by expanding short bullets or retaining low-signal detail so every bullet occupies similar space.
- Allow a bullet to approach 220 only when the additional supported mechanism, constraint, scale, or outcome materially strengthens the same accomplishment.
- Before accepting a long bullet, remove repeated context and ask whether it contains two accomplishments that should occupy separate existing slots.
- Count rendered characters rather than LaTeX syntax: escaped forms such as `\%` and `\&` count as one visible character each, while commands such as `\textbf{}` contribute only their visible contents.
- In CV edit mode, do not rely on estimation: run the target-specific length check and revise until both the 220-character per-bullet ceiling and 180-character maximum block average pass.
- Use `$cv-fit-bullets` in a separate request when the user wants one-line bullets, an exact rendered line count, or a one-page CV.

## LaTeX

- In CV edit mode, change only the inner content of each existing `\resumeItem{...}` slot and preserve every wrapper and surrounding byte.
- In prompt-only mode, preserve any pasted `\resumeItem{...}` wrappers and modify only their inner text.
- Do not add new `\textbf{...}` emphasis while building content. Importance should be evident from selection and sentence structure; use `$cv-bold-highlights` as a separate formatting pass.
- Escape literal `%`, `&`, `_`, `#`, and `$` characters.
- Keep each replacement as one logical bullet and preserve the existing bullet count and order.

## Guidance basis

- Google recommends showing an accomplishment, a measurement when available, and how it was achieved.
- MIT career guidance recommends strong action verbs, relevant tasks, outcomes, metrics, and one-to-two-line final resume bullets. This skill deliberately handles the richer content-first draft before final fitting.
