# CV parser rules

## Purpose

Provide a readable representation of a Jake's Resume-style LaTeX CV for the skill to understand, while retaining structural information for precise target selection and safe edits. Modified templates are supported only where their commands and structure can be interpreted reliably.

Parsing extracts content; it does not rewrite, improve, summarise, tailor, or correct candidate facts. The user's AFTER example specifies the desired presentation, not replacement content for main.tex.

## Input and scope

Read the selected CV source, initially `workspace/main.tex`. Extract all visible CV content, including contact information, education, experience, projects, and skills. Full-content extraction is separate from edit eligibility: cv-tailor changes only selected existing resumeItem bodies.

Do not read context documents, execute LaTeX, or fetch hyperlink destinations during source parsing. Compile separately for mandatory rendered layout verification.

## Output contract

The version 1 fields, node types, and synthetic reference outputs are defined in [cv-parser-output.md](cv-parser-output.md).

## Readable view

Produce plain text in source reading order:

- Name and contact information at the top.
- Clearly separated section headings.
- Entry headings with their dates, organisation, qualification, location, or technology text as applicable.
- One logical paragraph per bullet, prefixed with a bullet marker.
- Supporting lines such as relevant modules.
- Labelled skill lists.

Use blank lines between sections and entries. Uppercase section headings may be used as presentation styling without altering their identity. Preserve meaningful punctuation, spelling, numbers, units, dates, qualifiers, and associations between facts and their entry.

Do not copy screenshot/PDF wrapping into the readable view. Source newlines within prose become appropriate whitespace; each bullet remains one logical paragraph. This view does not indicate rendered line count.

## Content extraction rules

| Source construct | Readable representation |
| --- | --- |
| `\section{...}` | Section heading, preserving its text and order |
| `\resumeSubheading{a}{b}{c}{d}` | First heading row `a` with `b`; second row `c` with `d`, matching this template's definition |
| `\resumeProjectHeading{a}{b}` | Project heading text and any non-empty second argument |
| `\resumeSubSubheading{a}{b}` | Subheading and associated date/text; retain parent relationship |
| `\resumeItem{...}` | One bullet with its full visible content |
| `\resumeLine{...}` | Supporting content attached to the corresponding entry |
| `\textbf{...}`, `\textit{...}`, `\emph{...}`, `\underline{...}` | Inner visible text; remove styling wrappers from the readable view |
| `\href{destination}{label}` | Visible label; retain destination separately if needed, without fetching it |
| `\url{...}` | Visible URL |
| `\%`, `\&`, `\_`, and other supported literal escapes | Corresponding visible character |
| `--`, `---` | En dash and em dash respectively in supported text contexts |
| `$|$`, `$\sim$` | `|` and `∼` respectively |
| `\\` | Structural line break where applicable, such as contact or skills rows |
| Nonbreaking space `~` | Readable space; do not confuse it with the mathematical approximation symbol |

Interpret commands with balanced arguments, including nested formatting. Do not use global string stripping that can discard visible content or confuse escaped braces with structural braces.

The observed template defines heading arguments in two rows. Different definitions must be detected or reported rather than silently assigned the wrong meaning. Do not assume every resumeSubheading is employment: education uses the same command.

## Excluded presentation machinery

Omit document class declarations, package imports, macro definitions, margin/font settings, spacing commands, list wrappers, decorative rules, and document/environment delimiters from the readable view. Preserve the visible content inside supported wrappers.

Ignore actual LaTeX comments and commented-out entries. Respect escaped percent signs and LaTeX comment newline behaviour; deleting a comment must not accidentally join or split visible words.

Parse document content rather than matching example commands inside macro definitions. Do not discard an unknown construct merely because it resembles formatting.

## Structural representation for editing

The readable view is accompanied by structured source metadata. It must retain:

- Source identity and content fingerprint.
- Parser and output-format version.
- Ordered sections, entries, and bullets, with identifiers unique within the parsed source.
- Original labels and entry relationships, including repeated names.
- Exact raw LaTeX bullet bodies and their source ranges.
- Original formatting, including bold spans, available through raw source even when absent from plain text.
- Diagnostics for unsupported or ambiguous structures.

Plain text alone is not an editing format. Do not regenerate the full CV from the readable view. The edit layer replaces verified source spans and preserves unrelated source bytes.

Ranges from main.tex must never be applied directly to tailored.tex: previous tailoring may have changed offsets. Resolve and validate the destination's structure separately before applying edits. Identifiers are not assumed stable across structural source changes.

## Empty and ambiguous content

Represent empty bullet commands as existing empty slots; do not omit them or invent text. Preserve bullet counts and order.

Keep duplicate entry names distinct using their enclosing section and additional heading information. Target resolution asks for clarification when a request cannot identify a unique entry.

Malformed braces, incomplete commands, or unsupported structures must produce actionable diagnostics. Never present a silently truncated extraction as a complete CV. If a target's boundaries or content cannot be established reliably, it is not safe to edit.

## Source locations

Read source as bytes and decode as UTF-8 without normalising newlines. Reject invalid UTF-8 with a diagnostic. Record source locations before transforming text into the readable view.

For each section, entry, heading field, supporting line, and bullet, retain its source span. For bullets, retain both the complete command span and its editable body span, excluding the command and outer braces. Nested formatting remains inside the body span.

- Byte offsets are zero-based, half-open ranges: `[start_byte, end_byte)`. They address the original byte buffer, not a decoded string.
- Line and column positions are one-based. Columns count Unicode code points, not bytes or display cells; tabs count as one code point. End positions are exclusive. CRLF is treated as one newline, while original bytes remain unchanged.
- An empty bullet body has equal start and end offsets.
- Keep raw LaTeX and readable text alongside locations. Validate that the recorded byte slice equals the UTF-8 encoding of the raw LaTeX before replacement.

Line and column positions support diagnostics. Byte spans support exact edits. Apply multiple non-overlapping replacements from the highest byte offset downward so earlier positions remain valid during a batch. Encode replacements as UTF-8 and preserve all bytes outside their spans.

Locations belong only to the source snapshot identified by their hash. Revalidate the destination immediately before writing; reject stale edits rather than applying old offsets. After a successful edit, invalidate the old destination cache and regenerate it before another read or edit. Never transfer main.tex offsets to tailored.tex.

## Cache layout

Store derived data under the already ignored workspace directory:

```text
workspace/.cache/cv/
├── main.json
├── main.txt
├── tailored.json
└── tailored.txt
```

Create each pair only when its source is parsed. `main.json` and `tailored.json` contain structured extraction, source metadata, diagnostics, and the full readable text. The corresponding `.txt` file is a convenience view generated from that JSON for AI reading; it is never an independent authority. A missing or altered text view is regenerated from validated JSON.

The JSON envelope contains:

- `schema_version`: integer version of the saved data contract.
- `parser_version`: explicit version of extraction and interpretation behaviour.
- `source_path`: canonical absolute source path, preventing reuse for a different checkout or file.
- `source_sha256`: SHA-256 of the exact original file bytes, including whitespace and line endings.
- `readable_text`: the full plain-text view.
- `sections`: ordered structural data and source locations.
- `diagnostics`: extraction issues; failed or incomplete extraction is not a valid successful cache.

Main and tailored records are independent. Their identifiers are unique within a source snapshot and are not durable cross-file matching keys.

## Cache freshness and lifecycle

On every parse request:

1. Read the source bytes and calculate their SHA-256 hash.
2. Validate existing JSON structure, source path, source hash, parser version, and schema version.
3. Reuse a complete matching record; otherwise parse the current bytes again.
4. Publish successful JSON through a temporary file and atomic replacement, then regenerate the text view. Validate the JSON/text pair before exposing it to the skill; an interrupted write must not expose stale text as current.

Use hashes rather than file modification times or file sizes as the freshness authority. Bump `parser_version` when extraction rules or interpretation change, even if the JSON shape does not. Bump `schema_version` when consumers need a different data contract. Cosmetic code changes need not invalidate the cache.

Missing, malformed, incompatible, or stale cache files trigger regeneration. An extraction failure must be reported rather than falling back to a stale successful result. Deleted source files cannot be read through their old cache. Cache-write failure may use a fresh in-memory result with a clear diagnostic; it must not make stale disk output appear current.

The cache is disposable, contains private CV data, and is never committed or used as independent claim evidence. Deleting it is safe: the next request rebuilds it from the source. Public fixtures and examples use synthetic data only.

## Verification

Use synthetic fixtures to verify:

- Complete readable extraction of contact, education, experience, projects, and skills.
- Nested styling, escaped literals, symbols, hyperlinks, and source line wrapping.
- Ignoring comments, preamble definitions, and commented-out sample entries.
- Correct heading associations, duplicate names, and empty slots.
- Exact source-span correspondence and unchanged source after parsing.
- Explicit failures for malformed and unsupported input.
- Cache reuse only when source identity, exact bytes, parser version, and schema version match.
- Regeneration for corrupt JSON, stale or missing text views, and interrupted cache writes.
- UTF-8 multibyte characters, CRLF files, empty spans, and descending batch replacements.
- Stale-destination rejection and independent main/tailored records.

Rendered line limits and visual balance require the separate compiler workflow; parsing success does not establish PDF correctness.

## Implementation decisions still to resolve

- Public parser interface; the version 1 output schema is defined in cv-parser-output.md.
- Supported macro variants and how to validate their definitions.
- Additional symbol/math support and unknown-command diagnostics.
- Handling included source files or user macros that contribute visible content.
