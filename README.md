# Codex CV Toolkit

A privacy-conscious toolkit for building, fitting, tailoring, highlighting, and scoring a LaTeX software-engineering CV with repository-scoped Codex skills.

## The three folders that matter

```text
templates/       tracked starter files; never put personal information here
workspace/       ignored working files; keep your real CV, vacancy, and evidence here
applications/    ignored job-specific CV copies created by the tailoring workflow
```

This separation is intentional. Files under `templates/` belong to the toolkit and appear in Git. Files under `workspace/` and `applications/` belong to you and are ignored.

## Quick start

Run once after cloning:

```bash
python3 scripts/setup_workspace.py
```

The command creates this ignored private workspace without overwriting anything:

```text
workspace/
├── main.tex
├── job-description.txt
└── context/
    ├── experience/example-company/evidence.md
    └── projects/example-project/evidence.md
```

Then:

1. Paste your complete LaTeX CV into `workspace/main.tex`.
2. Paste one complete vacancy into `workspace/job-description.txt`.
3. Optionally add factual notes or supporting files under the matching `workspace/context/experience/` or `workspace/context/projects/` folder.
4. Open the repository root in Codex so it discovers `AGENTS.md` and `.agents/skills/`.

If you used an older version of the toolkit, the setup command safely moves existing root-level `main.tex`, `job-description.txt`, and `cv-context/` inputs into `workspace/`. It never replaces an existing workspace file.

## Repository layout

```text
.
├── .agents/skills/          # The five CV skills
├── templates/               # Tracked public starter content
│   ├── main.tex
│   ├── job-description.txt
│   └── context/
├── workspace/               # Ignored private canonical inputs
├── applications/            # Ignored private job-specific copies
├── drafts/                  # Ignored tailoring drafts and previews
├── scripts/
│   ├── cv_drafts.py         # Target discovery, checks, and tailoring drafts
│   ├── cv_tex.py            # LaTeX bullet parsing and visible-text checks
│   ├── prepare_application.py
│   └── setup_workspace.py
├── tests/
└── AGENTS.md                # Privacy, evidence, and edit-scope guardrails
```

Do not edit or delete files under `templates/` during normal use. Restore an accidental template change with:

```bash
git restore templates
```

## Skills

| Skill | Use it for | Result |
|---|---|---|
| `$cv-build-bullets` | Create or strengthen truthful XYZ-style bullets | Direct edit to one named CV block, or a chat-only rewrite for pasted bullets |
| `$cv-fit-bullets` | Fit and visually balance existing bullets | Direct edit with a strict two-rendered-line maximum |
| `$cv-tailor-bullets` | Add supported job-relevant language | Private application copy plus a review draft |
| `$cv-bold-highlights` | Bold the most scan-worthy existing details | Direct `\textbf{}` edit without changing visible wording |
| `$cv-score` | Compare a CV with a vacancy | Read-only ATS and hiring-manager scores out of 100 |

There is no all-in-one skill or separate apply skill. Building, layout, tailoring, highlighting, and scoring remain separate so each change is easy to inspect.

## Select one exact CV block

List the available Experience and Projects targets:

```bash
python3 scripts/cv_drafts.py list workspace/main.tex
```

A file-targeted request should name:

- the CV path;
- `experience` or `project`; and
- the exact company or project name returned by the command.

Example:

```text
Use $cv-build-bullets on workspace/main.tex for experience "Example Company". Update only its resumeItem contents now.
```

The direct-edit skills preserve every heading, date, command, bullet slot, and unrelated byte. They only replace content inside the selected block's existing `\resumeItem{...}` commands.

## Build or rewrite bullets

For an existing CV block:

```text
Use $cv-build-bullets on workspace/main.tex for experience "Example Company". Strengthen its bullets using only their current facts.
```

For bullets pasted into chat, the same skill can work without touching the repository:

```text
Use $cv-build-bullets to strengthen these bullets using only their existing facts:

\resumeItem{Built ...}
\resumeItem{Improved ...}
```

The default ceiling is 220 visible characters per bullet and the target block average is at most 180. Bullets stay content-first: understandable to HR from the opening clause and technically credible to a senior engineer from one selective method or decision.

## Optional evidence

Current bullet wording and facts stated in your prompt are sufficient evidence for rewrites. Context is optional and never read automatically.

To authorise selected text evidence:

```text
Use $cv-build-bullets on workspace/main.tex for experience "Example Company". Also read its workspace/context folder.
```

A folder request permits relevant non-empty `.md` and `.txt` files for that target. PDFs remain opt-in: explicitly name the PDF or ask the skill to read PDFs. No skill may invent technologies, metrics, ownership, scale, outcomes, or causality.

## Fit the rendered layout

```text
Use $cv-fit-bullets on workspace/main.tex for experience "Example Company" in balanced-lines mode.
```

Available modes are `one-line`, `preserve-lines`, `n-lines` for one or two lines, `balanced-lines`, and `page-fit`. Every mode has a strict maximum of two rendered lines per bullet. Layout fitting requires a working LaTeX renderer because line count cannot be verified from character count alone.

In `balanced-lines` mode, the skill aims for mostly two-line bullets, naturally varied final-line lengths, and an occasional strong one-line bullet. It may add only supported detail from context you explicitly authorise.

## Add sparse bold highlights

```text
Use $cv-bold-highlights on workspace/main.tex for experience "Example Company".
```

The skill changes only formatting inside existing bullets. It prioritises meaningful metrics, differentiating mechanisms, central technologies, and strong validation signals without enforcing one bold span per bullet. LaTeX rendering is optional for this skill; if unavailable, review wrapping in Overleaf.

## Score and tailor for a job

Score the canonical CV against the current vacancy:

```text
Use $cv-score to score workspace/main.tex against workspace/job-description.txt.
```

Create a private, non-overwriting application copy:

```bash
python3 scripts/prepare_application.py example-company-software-engineer
```

This creates:

```text
applications/example-company-software-engineer/
├── main.source.tex
├── main.tex
└── job-description.txt
```

Tailor only the application copy:

```text
Use $cv-tailor-bullets on applications/example-company-software-engineer/main.tex for experience "Example Company". Create a draft against its job description.
```

The tailoring skill may add only supported keywords and leaves unsupported requirements as honest gaps. It applies its own exact draft only after you explicitly request application.

## Checks

Inspect visible bullet text and character counts:

```bash
python3 scripts/cv_tex.py workspace/main.tex
```

Enforce the build limits for one exact block:

```bash
python3 scripts/cv_drafts.py check \
  --cv workspace/main.tex \
  --kind experience \
  --target "Example Company" \
  --max-chars 220 \
  --max-average 180
```

Confirm private paths are ignored before committing:

```bash
git status --short
git diff --cached
git check-ignore -v workspace/ applications/ drafts/
```

Run the repository tests after changing scripts:

```bash
python3 -m unittest discover -s tests -v
```

Only anonymised templates, reusable skills, scripts, tests, and documentation belong in Git.
