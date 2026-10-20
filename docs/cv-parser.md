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

## Source-reading API

`scripts/cv_source.py` provides an immutable `SourceSnapshot`:

```python
from scripts.cv_source import SourceSnapshot

source = SourceSnapshot.read("workspace/main.tex")
source.sha256                    # Hash of the original bytes
source.text                      # UTF-8 text with original newlines
source.raw                       # Unmodified bytes
source.span_from_characters(0, 5) # Scanner offsets to JSON-ready locations
```

`byte_offset(character_offset)` and `character_offset(byte_offset)` translate between decoded-string and original-byte boundaries. `position(byte_offset)` returns a one-based line/column; `span(start_byte, end_byte)` returns the contract's half-open range. `slice_text(start_byte, end_byte)` extracts exact source content. Empty spans and the end-of-file boundary are valid.

Negative, reversed, out-of-bounds, and mid-UTF-8-character ranges are rejected. Invalid UTF-8 raises `SourceEncodingError` with code `invalid_utf8`, the path, and offending byte range, without including private source text. File access errors propagate; no cache or fallback is consulted by this layer.

LF, CRLF, and standalone CR count as line breaks. Within a CRLF pair, the boundary after CR remains on the preceding line; the next line starts after LF. Tabs and combining characters each count as one code point. A UTF-8 BOM is preserved as U+FEFF and contributes to source offsets; any treatment as non-visible content belongs to extraction.

A snapshot never changes when the on-disk file changes. Callers must read a fresh snapshot to compare hashes before reusing source locations. This layer does not parse LaTeX, cache results, or modify source files.

## LaTeX structure API

`scripts/cv_latex.py` exposes `scan_latex(snapshot)`, returning an immutable tuple of `LatexNode` objects. Node kinds are `command`, `control_symbol`, `group`, `comment`, `whitespace`, `math_delimiter`, and `text`.

Each node records exact start/end byte offsets. `raw(snapshot)` and `span(snapshot)` recover its original text and line/column locations. Group nodes additionally hold ordered children and a body span excluding the braces, including zero-width empty bodies. Concatenating top-level raw nodes reconstructs the complete input byte-for-byte; group children reconstruct their body. Nodes must be used with the snapshot from which they were scanned.

Commands contain an ASCII-letter control word without the backslash. Backslash followed by a non-letter becomes a control symbol; escaped braces, percent signs, and dollar signs do not act as structural delimiters. Comments include their terminating LF, CRLF, or CR, if present. They are retained as opaque nodes, so later extraction can omit them without injecting an extra newline. Whitespace following a comment is retained separately for later TeX whitespace interpretation.

Commands and following brace groups remain siblings: this scanner does not guess argument ownership. Stars and square brackets remain text until a command-aware layer interprets them. Dollar delimiters are recorded without interpreting or validating mathematical expressions. Macro definitions in the preamble remain syntax; the extraction layer must distinguish them from document content.

Unbalanced groups, trailing backslashes, and excessive nesting raise `LatexSyntaxError` with a stable code, path, and source span. The scanner uses an explicit stack with a default maximum group depth of 128. It rejects known lexical mode changes (`verb`, `catcode`, `makeatletter`, `ExplSyntaxOn`). Unknown ordinary commands are preserved, not silently discarded.

This is a bounded CV syntax scanner, not a TeX interpreter. Environment validation, verbatim-like environment rejection, conditional processing policy, macro signatures, optional arguments, and visible-text interpretation belong to command-aware extraction. A successful scan alone does not certify a document as supported or safe to edit. No LaTeX execution or source mutation occurs.

## Structural extraction API

`scripts/cv_structure.py` exposes `extract_structure(snapshot)`. It returns a `StructureResult` with source path/hash, ordered header content, and ordered sections. This is an intermediate representation: heading fields and bullet bodies have exact raw LaTeX and source spans, but readable `text` fields are added in the next extraction stage. It must not be published as a completed cache envelope.

The extractor recognises section commands, four-argument resumeSubheading entries, two-argument resumeProjectHeading entries, two-argument resumeSubSubheading child entries, resumeItem slots, and resumeLine supporting text. Argument groups may contain nested formatting and may be separated by whitespace or comments. Empty arguments and bullets remain present. Section and entry spans follow the output contract.

Entries are assigned source-order IDs (`s1.e1`, `s1.e2`); child roles have nested IDs such as `s1.e1.e1`. Repeated labels are never deduplicated. A subordinate heading attaches to the most recent top-level entry in the current section; a new section clears this relationship. This stage does not resolve user-supplied names or select between duplicates.

Document markers must form one begin/end pair. Macro definitions and sample commands inside preamble groups are excluded from entry discovery. The extractor checks list wrappers and supported `center`, `itemize`, and `enumerate` environments for balanced, properly nested boundaries. Other body environments, includes, conditional commands, and body macro definitions are rejected with source-located diagnostics. Starred/optional structural command variants are not yet supported and fail explicitly.

Uninterpreted visible content is retained in intermediate `raw` nodes with source spans, rather than dropped. Structural commands nested inside an opaque content group are rejected instead of being guessed as entries. Unsupported ordinary commands retained here must be resolved or rejected by the readable-text stage. The readable-text layer validates supported structural macro signatures and layout bodies before producing the completed output; structural extraction alone does not perform arbitrary macro expansion or certify edits.

Tests compare the reference fixture's entry structures against its independently authored contract, excluding only readable text. Additional cases cover duplicate labels, parent/child roles, empty sections and slots, comments, nested formatting, and invalid structural boundaries.

## Cache layout

Store derived data under the already ignored workspace directory:

```text
workspace/.cache/cv/
├── main.json
├── main.txt
├── tailored.json
└── tailored.txt
```

Create each pair only when its source is parsed. `main.json` and `tailored.json` contain structured extraction, source metadata, diagnostics, the full readable text, and a cache-only `cache_sha256` checksum. The corresponding `.txt` file is a convenience view generated from that JSON for AI reading; it is never an independent authority. A missing or altered text view is regenerated from validated JSON.

The public JSON envelope contains:

- `schema_version`: integer version of the saved data contract.
- `parser_version`: explicit version of extraction and interpretation behaviour.
- `source_path`: canonical absolute source path, preventing reuse for a different checkout or file.
- `source_sha256`: SHA-256 of the exact original file bytes, including whitespace and line endings.
- `readable_text`: the full plain-text view.
- `sections`: ordered structural data and source locations.
- `diagnostics`: extraction issues; failed or incomplete extraction is not a valid successful cache.

The on-disk `cache_sha256` hashes canonical JSON (sorted keys, compact separators, UTF-8) excluding the checksum itself. It detects accidental payload corruption, not malicious tampering. It is removed from the public parser result. Cached nodes are also checked for schema shape, source slices, unique IDs, ordered containment, and readable-view consistency.

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

## Readable extraction and supported scope

`scripts/cv_text.py` exposes `parse_cv(snapshot)`, returning the complete version 1 contract. It adds readable text to the structural representation, preserves empty bullet slots, converts supported symbols, and rejects unknown visible commands with located diagnostics. The original reference JSON and text fixtures remain unchanged and are compared against actual output in tests.

Supported content includes nested bold/italic/emphasis/underline and basic font wrappers, heading fields, resumeLine, hyperlink labels, literal URLs, escaped punctuation, common sizing declarations, line breaks, and the inline symbols used by the template. Comments and control-word delimiter whitespace are interpreted without injecting words or spaces. Complex mathematics, custom visible macros, starred structural headings, optional heading arguments, included document bodies, and arbitrary environments are not supported.

Structural macro definitions may use supported font wrappers, item/list and tabular layout, spacing, and their parameters once in order. Reordered, missing, duplicated, or literal-injecting definitions are rejected. This is a bounded template reader, not a TeX interpreter: it does not resolve packages or execute preamble code. A declaration's physical alignment and wrapping remain the compiler's responsibility.

Raw header/section content is converted to text nodes; top-level explicit line breaks create separate nodes. A formatting group containing multiple lines remains one text node with embedded newlines and a span covering the group. This retains an exact source correspondence without inventing overlapping wrapper spans.

## Cache API

`scripts/cv_cache.py` exposes `load_cv(path, use_cache=True)`, returning the public record, a `hit`/`rebuilt`/`disabled` status, and any cache-write warnings. The caller always consumes the current returned record, never reads a text view blindly. Missing/deleted/invalid source fails without returning stale cached results. Source bytes are checked again before and after publishing cache files.

Caching is restricted to `workspace/main.tex` and `workspace/tailored.tex`. Other paths require no-cache mode. Cache directory/file symlinks are rejected. Writes use temporary files with owner-only permissions followed by atomic replacement; interrupted text-view writes are repaired on the next call. Concurrent source modification raises an error and requires a retry. Consumers must still validate source hashes immediately before later edits.

## Public interface

See [cv-parser-usage.md](cv-parser-usage.md) for commands, exit behaviour, and examples. Both commands are read-only with respect to source CV files. No editing, tailoring, compiler integration, or context-document ingestion is implemented by this parser.
