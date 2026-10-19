# CV parser output contract — version 1

## Reference example

The executable contract fixtures are entirely fictional:

- [LaTeX input](../tests/fixtures/parser/synthetic.tex)
- [Readable output](../tests/fixtures/parser/expected.txt)
- [Structured output](../tests/fixtures/parser/expected.json)

These are expected outputs for future parser implementation, not outputs from a parser that already exists. The source hash and locations are calculated from the exact fixture bytes. The example uses `/synthetic/workspace/main.tex` as an intentionally fictional absolute path; real output uses the resolved input path. Tests of a future parser substitute only this path when comparing its output with the expected fixture.

## Envelope

All listed fields are required. Successful output is one UTF-8 JSON object.

| Field | Type | Meaning |
| --- | --- | --- |
| `schema_version` | integer | `1`; identifies this data contract |
| `parser_version` | string | Extraction behaviour version, initially `"1"` |
| `source_path` | string | Canonical absolute input path |
| `source_sha256` | string | Lowercase 64-character SHA-256 of original bytes |
| `readable_text` | string | Complete readable CV; matches text output exactly |
| `header` | array of text nodes | Visible material preceding the first section |
| `sections` | array of section nodes | Sections in source order |
| `diagnostics` | array | Non-fatal diagnostics; empty for the reference fixture |

Do not include generation timestamps: unchanged input and parser behaviour should yield deterministic data. Invalid or incomplete extraction is an error, not a successful envelope or a cacheable partial CV.

## Source spans

Each `span` contains `start_byte`, `end_byte`, `start`, and `end`. Byte offsets are zero-based and half-open. `start` and `end` each contain one-based `line` and `column`; end is exclusive. Columns count Unicode code points, not UTF-8 bytes. CRLF counts as one line break. Ranges refer to original source, before whitespace or formatting conversion.

All nodes have a unique snapshot-local `id` and a `kind`. IDs use source ordinals rather than content-derived names, keeping duplicate names distinct. They must not be reused as cross-file identities or assumed stable after structural changes.

## Node types

### Text and field nodes

Required fields: `id`, `kind`, `raw_latex`, `text`, `span`.

- `text` nodes represent header lines, supporting entry lines, and standalone section content such as skills.
- `field` nodes represent a section label or a heading argument. Heading fields also have a one-based `argument_index`.
- `raw_latex` equals the decoded source slice exactly. `text` contains its readable interpretation.
- A supporting line's span includes its command. A heading field's span excludes its outer argument braces.
- Links retain their destination in `raw_latex`; the readable view contains their visible label. No network access is needed.

### Heading nodes

Required fields: `id`, `kind`, `raw_latex`, `text`, `span`, `command`, `fields`.

`command` omits the leading backslash. `fields` preserves command argument order, including empty arguments. The entire command is retained in `raw_latex`. A four-argument subheading renders arguments 1 and 2 on one logical line, then 3 and 4 on the next. A project heading renders its two arguments on one line, omitting empty text. Join non-empty fields within a row with one space.

Do not hardcode employer/role semantics into argument positions across all sections: the same command can describe education. Entry identity can be resolved using section, command, and the preserved heading fields.

### Bullet nodes

Required fields: `id`, `kind`, `raw_latex`, `text`, `span`, `command`, `body_latex`, `body_span`.

`span` covers the full resumeItem command; `body_span` covers only the contents of its braces. `body_latex` must equal that exact decoded source slice. Formatting remains in the body; readable `text` removes supported styling. An empty body has equal byte endpoints and empty text. It still occupies one slot.

### Entry nodes

Required fields: `id`, `kind`, `heading`, `span`, `items`.

`items` contains ordered bullet nodes, text nodes, or nested entry nodes. Nested entries represent subordinate roles and inherit their parent relationship from containment. Entry spans begin at the heading command and end at the last content item, or the heading end if no content exists. They may enclose list wrappers and comments; trailing list-closing machinery is not part of this tight content span. Entry spans are informational, not replacement boundaries.

### Section nodes

Required fields: `id`, `kind`, `title`, `span`, `items`.

`title` is a field node preserving the section label. `items` contains ordered entries or text nodes. Section spans begin at the section command and end at the next section command, or the start of end-document for the last section. Only validated bullet body spans are editing boundaries.

## Readable text conventions

- Preserve wording and source order; do not rewrite facts.
- Render section headings in uppercase, while structured title text retains original case.
- Separate header and sections, section headings and content, and adjacent entries with one blank line.
- Keep each bullet on one logical line, prefixed with `• `; an empty slot is a bare `•` line, never an invented description.
- Keep header contact details on their logical source rows. Use actual visible separators.
- Render supporting lines immediately after their entry heading or preceding item, in source order.
- Use LF newlines and exactly one final newline for a non-empty readable view, regardless of source line endings.
- Preserve original source newlines and other bytes only in raw fields and locations, not in prose line wrapping.

No font widths, rendered line counts, or PDF coordinates belong in this extraction schema. Those require separate rendering.

## Diagnostics and failures

A diagnostic has `code` (stable string), `severity` (`warning` or `error`), `message` (human-readable string), and `span` (source span or null when unavailable). A successful envelope may contain warnings only if all visible content and boundaries are still faithfully represented. Empty slots are valid data, not extraction errors.

Malformed syntax, unsupported visible commands, or uncertain extraction produce a failure with diagnostics. A failure has no successful readable CV and must not replace a valid cache with partial data. The CLI error transport will be defined with the public interface.

## Verification for this task

Contract tests verify fixture SHA-256, exact raw source slices, Unicode-aware positions, nested span containment, unique IDs, empty slots, and equality of JSON readable text with the text file. These tests validate the authored contract, not parser behaviour. Future parser tests must compare actual output against these independently authored expectations.
