# Repository instructions

## Privacy and evidence

- Treat `workspace/main.tex`, `workspace/job-description.txt`, and `workspace/context/` as the user's actual private inputs. Never redirect them to tracked files under `templates/`.
- Keep personal CVs, evidence, job descriptions, application copies, drafts, previews, and backups in the ignored paths documented in `README.md`.
- Never copy personal or employer-confidential material into tracked examples.
- Use only pasted or current bullet wording, explicit user facts, and context files the user explicitly authorises as claim evidence. Never invent metrics, technologies, scale, ownership, outcomes, or causality.
- Do not inspect or read `workspace/context/` merely because it exists. Read context only when the user asks. Never open a PDF unless the user explicitly asks to read PDFs or names the exact PDF.

## Bullet workflow

- Every bullet-writing request that targets a CV file must identify one CV path, one kind (`experience` or `project`), and one exact target name from `python3 scripts/cv_drafts.py list <cv-path>`.
- Prompt-only building or strengthening may rewrite bullets pasted in chat without repository discovery or a JSON draft. Preserve pasted `\resumeItem{...}` wrappers and change only their contents.
- CV-targeted `$cv-build-bullets` requests edit the named CV immediately. They must replace only the contents of existing `\resumeItem{...}` commands in the selected target and must not create a review draft or wait for approval.
- `$cv-build-bullets` uses a default hard ceiling of 220 visible characters per bullet and a target block average of 175–180. A CV edit is incomplete until the target-specific check confirms every bullet is at most 220 and the block average is at most 180; never add filler to make a complete bullet reach 175.
- Keep one primary accomplishment per bullet. Split independently valuable achievements across existing slots when possible, without changing the block's `\resumeItem` count.
- Every build bullet must pass both audience checks: an HR recruiter understands the accomplishment and value from the opening clause, while a senior engineer sees one selective, concrete technical method or decision. Never substitute stack density for engineering credibility.
- `$cv-fit-bullets` edits the named CV immediately and may replace only existing `\resumeItem{...}` contents in the selected target. It must not create a JSON draft, preview TeX file, review copy, or separate approval step.
- `$cv-bold-highlights` edits the named CV immediately and may add only `\textbf{...}` inside existing `\resumeItem{...}` contents in the selected target. Visible wording must remain identical, and it must not create draft or preview files. Rendering is optional; never require or recommend installing MacTeX solely for bolding, and report wrapping as unverified when no renderer exists.
- Tailoring may still produce preview drafts and may apply its own exact draft through `python3 scripts/cv_drafts.py apply` only after the user explicitly asks it to do so; no separate apply skill is used.
- `$cv-fit-bullets` has a hard maximum of two rendered lines per bullet in every mode. Never complete a three-line fitted bullet; if rendering is unavailable, stop before editing because the limit cannot be verified.
- In `balanced-lines` mode, reject a uniformly sparse block: for at least three two-line bullets, target at least 60% average final-line fill and one ending around 75% or more. Expand only from current wording, explicit user facts, or context files the user explicitly authorised; otherwise do not modify the CV.
- Preserve commands, bullet count, order, headings, dates, chronology, comments, whitespace outside the selected bullet bodies, and every unrelated byte of the CV.
- Treat `workspace/main.tex` as canonical. Job-specific tailoring targets only a private `applications/<slug>/main.tex` copy.
- Scoring is read-only and must not modify the CV or draft.

## Verification

- Run `python3 -m unittest discover -s tests -v` after changing scripts.
- Run the official skill quick validator after changing any folder under `.agents/skills/`.
- When layout matters, validate rendered output. `$cv-fit-bullets` requires rendered verification; `$cv-bold-highlights` uses it only when already available and otherwise directs the user to review wrapping in Overleaf. Other producing skills may validate a generated preview. State clearly when a LaTeX renderer is unavailable.
