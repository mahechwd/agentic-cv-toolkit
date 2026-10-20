"""Extract CV structure without rendering visible text or modifying source.

The result is an intermediate representation, not the final readable/cache
contract. Uninterpreted content is retained for the text-extraction stage.
"""
from dataclasses import dataclass

from scripts.cv_latex import LatexNode, LatexSyntaxError, scan_latex
from scripts.cv_source import SourceSnapshot

TRIVIA = {'whitespace', 'comment'}
HEADINGS = {'resumeSubheading': 4, 'resumeProjectHeading': 2,
            'resumeSubSubheading': 2}
STRUCTURAL = {'section', 'resumeItem', 'resumeLine', *HEADINGS}
LIST_START = {'resumeSubHeadingListStart': 'headings', 'resumeItemListStart': 'bullets'}
LIST_END = {'resumeSubHeadingListEnd': 'headings', 'resumeItemListEnd': 'bullets'}
FORBIDDEN = {'input', 'include', 'newcommand', 'renewcommand', 'providecommand',
             'def', 'gdef', 'edef', 'xdef', 'let', 'csname', 'else', 'fi',
             'newenvironment', 'renewenvironment', 'endinput'}


@dataclass(frozen=True)
class StructureResult:
    source_path: str
    source_sha256: str
    header: tuple[dict, ...]
    sections: tuple[dict, ...]


def _fail(source, node, code, message):
    raise LatexSyntaxError(code, message, source,
                           source.character_offset(node.start_byte),
                           source.character_offset(node.end_byte))


def _arguments(source, nodes, index, count):
    """Read only known required brace arguments, preserving intervening trivia."""
    command = nodes[index]
    cursor = index + 1
    args = []
    for _ in range(count):
        while cursor < len(nodes) and nodes[cursor].kind in TRIVIA:
            cursor += 1
        if cursor >= len(nodes) or nodes[cursor].kind != 'group':
            _fail(source, command, 'missing_argument', 'Expected a required brace argument')
        args.append(nodes[cursor])
        cursor += 1
    return args, cursor


def _body(source, group):
    return source.slice_text(group.body_start_byte, group.body_end_byte)


def _check_opaque(source, node):
    """Never silently discover a CV entry hidden inside an unknown wrapper."""
    if node.kind == 'command':
        if node.name in FORBIDDEN or node.name.startswith('if'):
            _fail(source, node, 'unsupported_structure',
                  'Macro definitions, includes, and conditionals in document content are unsupported')
        if node.name in STRUCTURAL or node.name in LIST_START or node.name in LIST_END:
            _fail(source, node, 'nested_structure', 'Structural command inside a content group is unsupported')
        if node.name in {'begin', 'end'}:
            _fail(source, node, 'nested_environment', 'Environment boundary inside a content group is unsupported')
    for child in node.children:
        _check_opaque(source, child)


def extract_structure(source: SourceSnapshot) -> StructureResult:
    """Identify sections and heading relationships within one document body.

    IDs are ordinal and snapshot-local. Duplicate labels are never merged.
    Content outside recognised constructs remains raw, not silently discarded.
    """
    nodes = scan_latex(source)
    markers = []
    for i, node in enumerate(nodes):
        if node.kind == 'command' and node.name in {'begin', 'end'}:
            args, after = _arguments(source, nodes, i, 1)
            if _body(source, args[0]) == 'document':
                markers.append((node.name, i, after))
    if len(markers) != 2 or [m[0] for m in markers] != ['begin', 'end']:
        anchor = nodes[0] if nodes else LatexNode('text', 0, 0)
        _fail(source, anchor, 'document_boundary', 'Expected exactly one begin/end document pair')
    _, _, begin = markers[0]
    _, finish, after = markers[1]
    if any(n.kind not in TRIVIA for n in nodes[after:]):
        _fail(source, nodes[after], 'trailing_content', 'Content after end document is unsupported')
    body = nodes[begin:finish]
    header = []
    sections = []
    section = None
    parent = None
    active = None
    environments = []
    lists = []
    containers = []
    pending = []
    counters = {}

    def owner_items():
        if active is not None:
            return active['items'], active['id']
        if section is not None:
            return section['items'], section['id']
        return header, 'header'

    def widen(end):
        for entry in (parent, active):
            if entry is not None:
                entry['span'] = source.span(entry['span']['start_byte'], end)

    def flush():
        if not pending:
            return
        significant = [n for n in pending if n.kind not in TRIVIA]
        if significant:
            start, end = significant[0].start_byte, significant[-1].end_byte
            items, owner = owner_items()
            key = (owner, 'raw')
            counters[key] = counters.get(key, 0) + 1
            items.append({'id': f'{owner}.raw{counters[key]}', 'kind': 'raw',
                          'raw_latex': source.slice_text(start, end),
                          'span': source.span(start, end)})
            widen(end)
        pending.clear()

    def field(id, arg, argument_index=None):
        result = {'id': id, 'kind': 'field', 'raw_latex': _body(source, arg),
                  'span': arg.body_span(source)}
        if argument_index is not None:
            result['argument_index'] = argument_index
        return result

    i = 0
    while i < len(body):
        node = body[i]
        name = node.name if node.kind == 'command' else None
        if name in STRUCTURAL:
            flush()
            count = HEADINGS.get(name, 1)
            args, after = _arguments(source, body, i, count)
            for arg in args:
                _check_opaque(source, arg)
            end = args[-1].end_byte
            if name == 'section':
                if lists or environments:
                    _fail(source, node, 'section_in_container', 'Close list/environment before starting a section')
                if section is not None:
                    section['span'] = source.span(section['span']['start_byte'], node.start_byte)
                sid = f's{len(sections) + 1}'
                section = {'id': sid, 'kind': 'section',
                           'title': field(sid + '.title', args[0]),
                           'span': source.span(node.start_byte, end), 'items': []}
                sections.append(section)
                parent = active = None
            elif name in HEADINGS:
                if section is None:
                    _fail(source, node, 'heading_without_section', 'Entry heading requires an enclosing section')
                if any(kind == 'bullets' for kind, _ in lists):
                    _fail(source, node, 'heading_in_bullets', 'Close the bullet list before starting an entry')
                if name == 'resumeSubSubheading':
                    if parent is None:
                        _fail(source, node, 'orphan_subheading', 'Subheading requires a parent entry')
                    owner, prefix = parent['items'], parent['id']
                else:
                    owner, prefix = section['items'], section['id']
                number = sum(item['kind'] == 'entry' for item in owner) + 1
                eid = f'{prefix}.e{number}'
                hid = eid + '.heading'
                heading = {'id': hid, 'kind': 'heading', 'command': name,
                           'raw_latex': source.slice_text(node.start_byte, end),
                           'span': source.span(node.start_byte, end),
                           'fields': [field(f'{hid}.f{j}', arg, j) for j, arg in enumerate(args, 1)]}
                active = {'id': eid, 'kind': 'entry', 'heading': heading,
                          'span': source.span(node.start_byte, end), 'items': []}
                owner.append(active)
                if name != 'resumeSubSubheading':
                    parent = active
                widen(end)
            else:
                if active is None:
                    _fail(source, node, 'orphan_content', 'Bullet or supporting line requires an entry')
                kind = 'bullet' if name == 'resumeItem' else 'text'
                suffix = 'b' if kind == 'bullet' else 'line'
                number = sum(item['kind'] == kind for item in active['items']) + 1
                item = {'id': f"{active['id']}.{suffix}{number}", 'kind': kind,
                        'raw_latex': source.slice_text(node.start_byte, end),
                        'span': source.span(node.start_byte, end)}
                if kind == 'bullet':
                    item.update(command=name, body_latex=_body(source, args[0]),
                                body_span=args[0].body_span(source))
                active['items'].append(item)
                widen(end)
            i = after
            continue
        if name in LIST_START or name in LIST_END:
            flush()
            if name in LIST_START:
                kind = LIST_START[name]
                if kind == 'bullets' and (active is None or any(k == 'bullets' for k, _ in lists)):
                    _fail(source, node, 'invalid_bullet_list', 'Bullet list requires an entry and cannot nest')
                lists.append((kind, node))
                containers.append(("list", kind))
            elif not lists or lists[-1][0] != LIST_END[name] or not containers or containers[-1] != ('list', LIST_END[name]):
                _fail(source, node, 'list_mismatch', 'Mismatched list wrapper')
            else:
                lists.pop()
                containers.pop()
            i += 1
            continue
        if name in {'begin', 'end'}:
            flush()
            args, after = _arguments(source, body, i, 1)
            env = _body(source, args[0])
            if env not in {'center', 'itemize', 'enumerate'}:
                _fail(source, node, 'unsupported_environment', 'Unsupported document environment')
            if name == 'begin':
                environments.append((env, node))
                containers.append(("environment", env))
            elif not environments or environments[-1][0] != env or not containers or containers[-1] != ('environment', env):
                _fail(source, node, 'environment_mismatch', 'Mismatched environment boundary')
            else:
                environments.pop()
                containers.pop()
            # Keep enumitem options with their environment, not as visible prose.
            if name == 'begin' and after < len(body) and body[after].raw(source).startswith('['):
                while after < len(body) and ']' not in body[after].raw(source):
                    after += 1
                if after >= len(body) or not body[after].raw(source).endswith(']'):
                    _fail(source, node, 'unsupported_options', 'Unsupported environment options')
                after += 1
            # Preserve boundaries for the later visible-content layer.
            pending.extend(body[i:after])
            flush()
            i = after
            continue
        _check_opaque(source, node)
        pending.append(node)
        i += 1
    flush()
    if lists or environments:
        anchor = (lists or environments)[-1][1]
        _fail(source, anchor, 'unclosed_container', 'Unclosed list or environment')
    if section is not None:
        section['span'] = source.span(section['span']['start_byte'], nodes[finish].start_byte)
    return StructureResult(str(source.path), source.sha256, tuple(header), tuple(sections))
