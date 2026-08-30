# Codex CV Toolkit

A privacy-conscious toolkit for building, fitting, tailoring, highlighting, and scoring a LaTeX software-engineering CV with repository-scoped Codex skills.

## Working model

The toolkit keeps public starter files and private CV data separate:

```text
templates/       tracked starter files; never put personal information here
workspace/       ignored real CV, tailored CV, vacancy, and supporting evidence
```

Inside the private workspace, the two CV files have distinct jobs:

```text
workspace/main.tex       canonical CV; general improvements happen here
workspace/tailored.tex   current job-specific CV; tailoring happens only here
```

`main.tex` is never overwritten by the tailoring workflow. `tailored.tex` can be changed across several tailoring passes and reset from `main.tex` only when you explicitly request a fresh copy.

## Quick start

Run once after cloning:

```bash
python3 scripts/setup_workspace.py
```

It creates this ignored private workspace without overwriting existing files:

```text
workspace/
├── main.tex
├── tailored.tex
├── job-description.txt
└── context/
    ├── experience/example-company/evidence.md
    └── projects/example-project/evidence.md
```

Then:

1. Paste your complete LaTeX CV into `workspace/main.tex`.
2. Paste one complete vacancy into `workspace/job-description.txt`.
3. Optionally add factual notes under the matching `workspace/context/experience/` or `workspace/context/projects/` folder.
4. Open the repository root in Codex so it discovers `AGENTS.md` and `.agents/skills/`.

When tailoring starts, the helper refreshes `tailored.tex` automatically if it is still the untouched starter created during setup. Existing tailored work is otherwise preserved.

## Start a new tailored CV

For a new job description, first replace `workspace/job-description.txt`, then explicitly reset the job-specific copy:

```bash
python3 scripts/prepare_tailored.py --reset
```

This is the only normal workflow that replaces `workspace/tailored.tex` from `workspace/main.tex`. Without `--reset`, the command is non-destructive:

```bash
python3 scripts/prepare_tailored.py
```

It creates a missing tailored copy, refreshes an untouched starter, or reports `kept existing` for work already in progress.

## Repository layout

```text
.
├── .agents/skills/          # The five CV skills
├── templates/               # Tracked public starter content
├── workspace/               # Ignored private inputs and both working CVs
├── scripts/
│   ├── cv_blocks.py         # Target discovery and target-specific length checks
│   ├── cv_tex.py            # LaTeX bullet parsing and visible-text checks
│   ├── prepare_tailored.py  # Safe main-to-tailored copy/reset
│   └── setup_workspace.py
├── tests/
└── AGENTS.md                # Privacy, evidence, and edit-scope guardrails
```

Do not edit tracked files under `templates/` with personal information. Restore an accidental template change with:

```bash
git restore templates
```

## Skills

| Skill | Use it for | Default result |
|---|---|---|
| `$cv-build-bullets` | Create or strengthen truthful XYZ-style bullets | Direct edit to a named CV block |
| `$cv-fit-bullets` | Fit and visually balance existing bullets | Direct edit with a strict two-rendered-line maximum |
| `$cv-tailor-bullets` | Audit tailored bullets, recover canonical evidence, add supported job language, and recheck emphasis | Direct edit to `workspace/tailored.tex` only |
| `$cv-bold-highlights` | Bold the most scan-worthy existing details | Direct formatting edit without changing visible wording |
| `$cv-score` | Compare either CV with the vacancy | Read-only ATS and hiring-manager scores out of 100 |

There is no all-in-one skill, JSON review draft, application-folder workflow, or separate apply skill. Each producing skill updates its intended CV directly so the result can be reviewed in the `.tex` file or Overleaf.

## Select one exact CV block

List the Experience and Projects targets in either CV:

```bash
python3 scripts/cv_blocks.py list workspace/main.tex
python3 scripts/cv_blocks.py list workspace/tailored.tex
```

A file-targeted request should name:

- the CV path;
- `experience` or `project`; and
- the exact company or project name returned by `list`.

Direct-edit skills preserve every heading, date, command, bullet slot, and unrelated byte. They only replace content inside the selected block's existing `\resumeItem{...}` commands.

## Improve the canonical CV

Build or strengthen one block in the general CV:

```text
Use $cv-build-bullets on workspace/main.tex for experience "Example Company". Strengthen its bullets using only their current facts.
```

Fit its rendered shape:

```text
Use $cv-fit-bullets on workspace/main.tex for experience "Example Company" in balanced-lines mode.
```

Add semantic bolding:

```text
Use $cv-bold-highlights on workspace/main.tex for experience "Example Company".
```

The same build, fit, and bold skills can target `workspace/tailored.tex` when you explicitly name that path.

## Tailor for the current vacancy

Tailor one block directly in the separate job-specific CV:

```text
Use $cv-tailor-bullets for experience "Example Company" against workspace/job-description.txt.
```

The skill prepares `workspace/tailored.tex` when necessary, audits its selected block first, and then compares the matching block in `workspace/main.tex` for stronger evidence that may have been lost during earlier tailoring. After finalising the tailored wording, it rechecks existing bold spans and keeps, removes, moves, or adds sparse emphasis based on the accomplishment and vacancy without changing visible text. It changes only the selected tailored `\resumeItem{...}` bodies and confirms `workspace/main.tex` remained byte-for-byte unchanged. Follow-up requests continue editing the same tailored CV.

Only supported terms may be inserted. The skill prioritises exact ATS-relevant terminology from the job description, but does not promise a particular ATS result. Unsupported requirements are reported as gaps rather than added as claims. By default, tailoring preserves rendered line count and uses a maximum three-visible-character delta when rendering is unavailable. Add “keep the length the same” to your request to activate exact-length mode, which requires a zero visible-character delta for every bullet.

Company research is optional rather than automatic. Add “research the company” to the request to use current official company sources as secondary context for prioritising supported achievements; research never becomes evidence of candidate experience.

## Score before and after tailoring

If you do not name a CV path, `$cv-score` scores non-empty `workspace/tailored.tex` first and falls back to `workspace/main.tex` when the tailored file is missing or empty. An explicitly named path always takes priority.

Score the canonical CV:

```text
Use $cv-score to score workspace/main.tex against workspace/job-description.txt.
```

Score the tailored CV with the same rubric:

```text
Use $cv-score to score workspace/tailored.tex against workspace/job-description.txt.
```

Both scores are heuristic assessments rather than output from an employer's private ATS.

## Optional evidence

Current bullet wording and explicit facts in your prompt are sufficient evidence for rewrites. Context is optional and is never read merely because the folder exists.

To authorise selected text evidence:

```text
Use $cv-tailor-bullets for experience "Example Company". Also read its workspace/context folder.
```

A folder request permits relevant non-empty `.md` and `.txt` files for that target. PDFs remain opt-in: explicitly name the PDF or ask the skill to read PDFs. No skill may invent technologies, metrics, ownership, scale, outcomes, or causality.

## Checks

Inspect visible bullet text and character counts:

```bash
python3 scripts/cv_tex.py workspace/main.tex
python3 scripts/cv_tex.py workspace/tailored.tex
```

Enforce the build limits for one exact block:

```bash
python3 scripts/cv_blocks.py check \
  --cv workspace/main.tex \
  --kind experience \
  --target "Example Company" \
  --max-chars 220 \
  --max-average 180
```

Confirm private data is ignored before committing:

```bash
git status --short
git diff --cached
git check-ignore -v workspace/
```

Run the repository tests after changing scripts:

```bash
python3 -m unittest discover -s tests -v
```

Only anonymised templates, reusable skills, scripts, tests, and documentation belong in Git.
