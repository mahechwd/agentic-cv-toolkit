# Codex CV Toolkit

A privacy-conscious toolkit for building and tailoring a LaTeX software-engineering CV with repository-scoped Codex skills.

The central rule is simple:

```text
facts or optional evidence → direct \resumeItem edit → review main.tex → request another revision
```

`$cv-build-bullets`, `$cv-fit-bullets`, and `$cv-bold-highlights` edit one named Experience or Projects block immediately and may replace only the contents of its existing `\resumeItem{...}` commands. Tailoring may still create previews and apply its own reviewed result; there is no separate apply skill.

## Start here: where your content goes

Run this once after cloning:

```bash
python3 scripts/setup_workspace.py
```

It creates the following ignored private inputs when they are missing and never overwrites files that already exist:

| Private input | What you put there |
|---|---|
| `main.tex` | Paste your complete LaTeX CV, including its existing Experience and Projects headings and `\resumeItem{...}` slots |
| `job-description.txt` | Paste one complete job description, replacing all previous placeholder or vacancy text |
| `cv-context/experience/<company-slug>/` | Optionally add `.md`, `.txt`, and `.pdf` evidence for that employment entry |
| `cv-context/projects/<project-slug>/` | Optionally add `.md`, `.txt`, and `.pdf` evidence for that project |

Then open the repository root in Codex and invoke the appropriate skill. For example:

```text
Use $cv-build-bullets on main.tex for experience "Example Company". Read its cv-context folder and update only its resumeItem contents now.
```

`main.example.tex`, `job-description.example.txt`, and `cv-context.example/` are tracked public templates used to initialise a new clone. Do not paste personal information into them, and do not delete them during normal use. Because they are tracked, deleting one correctly appears in Git as an uncommitted deletion. Restore an accidental deletion with:

```bash
git restore main.example.tex job-description.example.txt cv-context.example
```

New untracked files accidentally placed under `cv-context.example/` are ignored as a privacy backstop, but the correct location for all real evidence remains `cv-context/experience/<company-slug>/` or `cv-context/projects/<project-slug>/`.

If you already created `main.tex`, `job-description.txt`, or `cv-context/`, the setup command prints `kept existing` and leaves their contents untouched.

## What is included

| Skill | Purpose | Output |
|---|---|---|
| `$cv-build-bullets` | Rewrite pasted bullets or directly fill/strengthen a named CV block using recruiter-readable, technically credible XYZ claims | Chat proposal or updated CV block |
| `$cv-fit-bullets` | Compress, expand, or visually balance one named block | Updated CV block |
| `$cv-tailor-bullets` | Add only job-relevant terms supported by evidence | Draft JSON + preview |
| `$cv-bold-highlights` | Add sparse `\textbf{}` around existing metrics or technologies | Updated CV block |
| `$cv-score` | Score ATS readiness and hiring-manager fit against a job description out of 100 | Read-only scorecard |

There is intentionally no all-in-one `customise-cv` skill. Content, layout, job tailoring, formatting, and scoring remain separate concerns, but applying an edit does not require a separate skill.

## Repository layout

```text
.
├── .agents/skills/          # Reusable repository-scoped workflows
├── AGENTS.md                # Repo-wide privacy and edit-scope guardrails
├── scripts/
│   ├── cv_drafts.py         # Target discovery, draft, preview, guarded apply
│   ├── cv_tex.py            # Visible-text and bullet-count checks
│   ├── prepare_application.py
│   └── setup_workspace.py   # Non-destructive private-input setup
├── tests/
├── main.example.tex         # Public CV template
├── job-description.example.txt
└── cv-context.example/      # Public evidence templates
```

The following local working files are ignored by Git:

```text
main.tex
job-description.txt
cv-context/
applications/
drafts/
```

This keeps personal details, employer evidence, vacancies, application copies, draft prose, previews, and backups out of commits by default.

## Setup

Requirements are Python 3.10 or newer and Codex in the ChatGPT desktop app, CLI, or IDE extension. A LaTeX distribution is optional but required for true rendered line-count and page verification. Open the repository root so Codex discovers `AGENTS.md` and `.agents/skills/`.

Run from the repository root:

```bash
python3 scripts/setup_workspace.py
```

The initializer copies the tracked templates only when each private destination is missing. It deliberately has no overwrite option.

Paste or maintain your real CV only in `main.tex`. Keep one existing `\resumeItem{...}` command for every bullet slot you want the toolkit to manage. A slot may be empty:

```tex
\resumeItem{}
```

Paste the complete vacancy into `job-description.txt`. Do not put personal, confidential, vacancy, or employer-internal material in tracked examples.

## Add evidence

Create one folder per CV target:

```text
cv-context/experience/example-company/
cv-context/projects/example-project/
```

Folder names should be lowercase slugs of the company or project name in `main.tex`. You may add non-empty `.md`, `.txt`, or `.pdf` sources with facts you can defend in an interview: contribution, mechanism, technology, scale, tests, reliability, security, performance, constraints, and outcomes.

Context is optional. `$cv-build-bullets` does not inspect `cv-context/` unless you explicitly ask it to use a named file or target folder. A general request to use a folder reads its `.md` and `.txt` evidence only; PDFs are opened only when you explicitly ask to read PDFs or name the exact PDF. Existing or pasted bullet wording and facts in your prompt are sufficient evidence for rewording, but never permit invented metrics, technologies, ownership, or impact.

To improve bullets pasted directly into chat without touching the repository:

```text
Use $cv-build-bullets to strengthen the bullets below using only their existing facts. Keep the same bullet count and do not read any context files.

\resumeItem{Built ...}
\resumeItem{Improved ...}
```

## Select exactly what to edit

List the editable targets in a CV:

```bash
python3 scripts/cv_drafts.py list main.tex
```

Example output:

```text
experience: Example Company — Software Engineer (4 bullets)
project: Example Project — Technology Stack (4 bullets)
```

Every writing request that targets a CV file should name:

- the CV path;
- `experience` or `project`; and
- the exact company or project name shown by `list`.

This prevents an agent from silently choosing the wrong section.

## Build directly in `main.tex`

Name the exact block and ask the skill to edit it:

```text
Use $cv-build-bullets on main.tex for experience "Example Company". Read its cv-context folder. Fill empty slots or strengthen existing bullets, and edit main.tex now.
```

Omit “Read its cv-context folder” to work from the block's current bullets and facts in your prompt only. Add “also read `<exact-file>.pdf`” only when that PDF is genuinely needed.

The skill:

- confirms one exact Experience or Projects target;
- preserves the number and order of `\resumeItem{...}` commands;
- replaces only their inner content;
- keeps every bullet within 220 visible characters by default and the block average at or below 180, naturally aiming for 175–180 without padding shorter bullets;
- splits independent achievements across existing slots rather than overloading one bullet;
- leads with plain-English value for HR, then adds only the technical evidence needed to impress a senior engineer;
- verifies the resulting LaTeX and visible character counts; and
- leaves every heading, date, command, comment, and unrelated section unchanged.

Review the result in `main.tex`. If you dislike the wording, tell `$cv-build-bullets` what to change and it will edit the same block again.

## Fitting bullets

Content-first bullets may intentionally span multiple lines. Fit one named block only after its content is strong:

```text
Use $cv-fit-bullets on main.tex for experience "Example Company". Fit the bullets directly to one line with a hard maximum of 112 visible characters.
```

Supported modes are:

- `one-line`: default hard ceiling of 112 visible characters;
- `preserve-lines`: keep a one- or two-line footprint and compress longer source bullets to two;
- `n-lines`: target a user-specified one- or two-line footprint;
- `balanced-lines`: create a rounded, ragged-right silhouette with mostly two-line bullets, varied final-line lengths, and occasional strong one-line bullets; and
- `page-fit`: keep the CV within its current page limit.

For example:

```text
Use $cv-fit-bullets on main.tex for experience "Example Company" in balanced-lines mode. Use the supplied screenshots as the visual-rhythm reference and preserve a natural mix of final-line lengths.
```

The skill edits only the selected `\resumeItem{...}` contents directly in the named CV, then compiles that CV into a temporary directory for verification. It does not create a JSON draft, preview TeX file, or approval step. Every mode has a strict two-rendered-line maximum; a three-line bullet must never remain in the completed edit. In `balanced-lines` mode, inspect the block as a whole: most bullets should occupy two lines, their final lines should taper to varied natural endpoints, and rare one-line bullets should remain concise rather than being padded. For blocks with at least three two-line bullets, the default density floor is approximately 60% average final-line fill with at least one ending around 75% or more.

When existing bullets do not contain enough truthful detail to reach that density, explicitly authorise the target's context folder:

```text
Use $cv-fit-bullets on main.tex for experience "Example Company" in balanced-lines mode. If needed, read its cv-context folder for supported detail, but do not read PDFs.
```

The skill may then use non-empty `.md` and `.txt` evidence from that target only. PDFs remain opt-in. If the available evidence still cannot support a fuller result, the skill does not modify the CV instead of inventing or padding content. Review the direct result in `main.tex` and request another revision if needed.

## Tailoring to a job

Paste one complete vacancy into ignored `job-description.txt`, then score the canonical CV:

```text
Use $cv-score to score main.tex against job-description.txt.
```

Create a non-overwriting private application workspace:

```bash
python3 scripts/prepare_application.py example-company-software-engineer
```

This creates:

```text
applications/example-company-software-engineer/
├── main.source.tex       # Immutable starting snapshot
├── main.tex              # Application working CV
└── job-description.txt
```

Tailor one named block at a time:

```text
Use $cv-tailor-bullets on applications/example-company-software-engineer/main.tex for experience "Example Company" against its job description. Create a draft only.
```

Supported equivalents and keywords may be proposed only when the relevant evidence or established bullet supports the same claim. Unsupported requirements remain honest gaps. Ask `$cv-tailor-bullets` to apply its exact reviewed draft, then rescore with the same `$cv-score` rubric.

## Sparse bold highlights

```text
Use $cv-bold-highlights on main.tex for experience "Example Company" and update the selected bullets directly.
```

This stage may add forms such as `\textbf{10M+ organisations}`, `\textbf{parallelized Camunda workflows}`, or `\textbf{Elasticsearch}` while keeping visible wording identical. It uses a variable zero-to-three spans per bullet, permits a fourth only when each span adds a distinct signal, and leaves low-signal bullets unbolded. The skill edits only the selected `\resumeItem{...}` contents and does not create a JSON draft, preview TeX file, or approval step. A LaTeX installation is optional: when a renderer already exists, the skill checks wrapping with temporary output; otherwise it completes the semantic bolding and asks you to review wrapping in Overleaf. You do not need to install MacTeX for this skill.

## Deterministic checks

Inspect active bullets and visible character counts:

```bash
python3 scripts/cv_tex.py main.tex
```

Enforce the build limits on one exact CV block:

```bash
python3 scripts/cv_drafts.py check \
  --cv main.tex \
  --kind experience \
  --target "Example Company" \
  --max-chars 220 \
  --max-average 180
```

This command exits unsuccessfully if a selected bullet is empty or over 220 visible characters, or if the selected block averages more than 180. It checks only the named block.

Enforce a 112-character ceiling:

```bash
python3 scripts/cv_tex.py drafts/previews/example-company.tex --max-chars 112
```

Compare visible text or character footprints:

```bash
python3 scripts/cv_tex.py drafts/previews/example-company.tex \
  --compare main.tex \
  --tolerance 3
```

Run the standard-library tests:

```bash
python3 -m unittest discover -s tests -v
```

## Compile and inspect

When a LaTeX toolchain is installed:

```bash
pdflatex -interaction=nonstopmode -halt-on-error \
  -output-directory=drafts/previews drafts/previews/example-company.tex
pdflatex -interaction=nonstopmode -halt-on-error \
  -output-directory=drafts/previews drafts/previews/example-company.tex
```

Inspect the PDF for line wrapping, page count, spacing, and machine-readable text before applying the draft.

## Truth policy

- Valid sources are pasted or current bullet wording, explicit user facts, and only the context files you explicitly ask the skill to read.
- A skills-section keyword alone does not prove use in a specific achievement.
- Unsupported job requirements are reported gaps, not text to insert.
- Never invent metrics, scale, technologies, ownership, business impact, or causality.
- Preserve qualifiers such as “estimated” whenever accuracy depends on them.

## Privacy check before committing

```bash
git status --short
git diff --cached
git check-ignore -v main.tex job-description.txt cv-context/ applications/ drafts/
```

Only anonymised templates, reusable skills, scripts, and tests belong in Git.

## Further reading

- [Official OpenAI documentation: build skills](https://learn.chatgpt.com/docs/build-skills)
- [Google resume-writing guidance](https://services.google.com/fh/files/misc/resume-writing-tips-for-veterans-2021.pdf)
- [MIT guidance on skills, metrics, and concise bullets](https://capd.mit.edu/resources/resumes-writing-about-your-skills/)
- [Oxford University CV guidance](https://www.careers.ox.ac.uk/cvs)
