"""Readable extraction for a deliberately bounded Jake-style LaTeX vocabulary."""
from copy import deepcopy
import re

from scripts.cv_latex import LatexSyntaxError, scan_latex
from scripts.cv_source import SourceSnapshot
from scripts.cv_structure import extract_structure, _arguments, _body, _fail, HEADINGS

PARSER_VERSION = '1'
SCHEMA_VERSION = 1
STYLES = {'textbf', 'textit', 'emph', 'underline', 'textrm', 'textnormal', 'textsf', 'texttt'}
DECLARATIONS = {'small', 'large', 'Large', 'LARGE', 'huge', 'Huge', 'tiny',
                'footnotesize', 'scriptsize', 'normalsize', 'scshape', 'bfseries',
                'itshape', 'normalfont', 'raggedright', 'centering'}
SYMBOLS = {'sim': '∼', 'textbar': '|', 'textasciitilde': '~', 'textbackslash': '\\',
           'textasciicircum': '^', 'LaTeX': 'LaTeX', 'TeX': 'TeX'}
ARITIES = {**HEADINGS, 'resumeItem': 1, 'resumeLine': 1,
           'resumeSubHeadingListStart': 0, 'resumeSubHeadingListEnd': 0,
           'resumeItemListStart': 0, 'resumeItemListEnd': 0}


def _validate_layout_body(source, nodes):
    """Permit layout around parameters, but reject injected visible wording."""
    i = 0
    while i < len(nodes):
        node = nodes[i]
        if node.kind == 'group':
            _validate_layout_body(source, node.children)
        elif node.kind == 'text':
            literal = re.sub(r'#[1-9]', '', node.raw(source))
            if literal and literal != '&':
                _fail(source, node, 'macro_visible_content', 'Structural macro adds unsupported literal content')
        elif node.kind == 'control_symbol':
            if node.name != '\\':
                _fail(source, node, 'macro_visible_content', 'Structural macro adds unsupported symbols')
        elif node.kind == 'command':
            name = node.name
            if name in STYLES:
                args, i = _arguments(source, nodes, i, 1)
                _validate_layout_body(source, args[0].children)
                continue
            if name in {'vspace', 'hspace'}:
                _, i = _arguments(source, nodes, i, 1)
                continue
            if name in {'begin', 'end'}:
                args, i = _arguments(source, nodes, i, 1)
                environment = _body(source, args[0])
                if environment not in {'itemize', 'tabular', 'tabular*'}:
                    _fail(source, node, 'macro_layout', 'Unsupported structural macro environment')
                if name == 'end':
                    continue
                def skip_trivia(cursor):
                    while cursor < len(nodes) and nodes[cursor].kind in {'comment', 'whitespace'}:
                        cursor += 1
                    return cursor
                i = skip_trivia(i)
                if environment == 'tabular*':
                    if i >= len(nodes) or nodes[i].kind != 'group':
                        _fail(source, node, 'macro_layout', 'Missing table width')
                    i = skip_trivia(i + 1)
                if i < len(nodes) and nodes[i].raw(source).startswith('['):
                    while i < len(nodes) and ']' not in nodes[i].raw(source):
                        i += 1
                    if i >= len(nodes) or not nodes[i].raw(source).endswith(']'):
                        _fail(source, node, 'macro_layout', 'Unsupported table/list options')
                    i = skip_trivia(i + 1)
                if environment in {'tabular', 'tabular*'}:
                    if i >= len(nodes) or nodes[i].kind != 'group':
                        _fail(source, node, 'macro_layout', 'Missing table column format')
                    i += 1
                continue
            if name not in DECLARATIONS | {'item', 'hfill'}:
                _fail(source, node, 'macro_layout', 'Unsupported command in structural macro')
        elif node.kind not in {'comment', 'whitespace'}:
            _fail(source, node, 'macro_layout', 'Unsupported structural macro syntax')
        i += 1


def _validate_definitions(source):
    """Check declared structural argument count/order; never expand user code."""
    nodes = scan_latex(source)
    seen = set()
    i = 0
    while i < len(nodes):
        node = nodes[i]
        if node.kind != 'command':
            i += 1
            continue
        if node.name == 'begin':
            args, _ = _arguments(source, nodes, i, 1)
            if _body(source, args[0]) == 'document':
                break
        if node.name.startswith('if') or node.name in {'def', 'gdef', 'edef', 'xdef', 'let', 'csname'}:
            _fail(source, node, 'unsupported_preamble', 'Unsupported conditional or primitive macro definition')
        if node.name not in {'newcommand', 'renewcommand', 'providecommand'}:
            i += 1
            continue
        # Unbraced definitions of unused formatting macros are not interpreted.
        j = i + 1
        while j < len(nodes) and nodes[j].kind in {'comment', 'whitespace'}:
            j += 1
        if j >= len(nodes):
            _fail(source, node, 'macro_definition', 'Incomplete macro definition')
        target = nodes[j]
        name = _body(source, target).strip().removeprefix('\\') if target.kind == 'group' else target.name
        if name not in ARITIES:
            if name in STYLES | DECLARATIONS | set(SYMBOLS) | {'href', 'url', 'section'}:
                _fail(source, node, 'macro_override', 'Redefining a supported visible command is unsupported')
            i += 1
            continue
        if name in seen:
            _fail(source, node, 'macro_redefinition', 'Repeated structural macro definition is unsupported')
        seen.add(name)
        j += 1
        while j < len(nodes) and nodes[j].kind in {'comment', 'whitespace'}:
            j += 1
        count = 0
        if j < len(nodes) and nodes[j].kind == 'text' and re.fullmatch(r'\[\d\]', nodes[j].raw(source)):
            count = int(nodes[j].raw(source)[1])
            j += 1
        while j < len(nodes) and nodes[j].kind in {'comment', 'whitespace'}:
            j += 1
        if count != ARITIES[name] or j >= len(nodes) or nodes[j].kind != 'group':
            _fail(source, node, 'macro_signature', 'Unsupported structural macro signature or default argument')
        definition = nodes[j]
        # Comments do not count as parameter use.
        def visible_syntax(n):
            if n.kind == 'comment':
                return ''
            return ''.join(visible_syntax(c) for c in n.children) if n.kind == 'group' else n.raw(source)
        parameters = re.findall(r'#([1-9])', visible_syntax(definition))
        if parameters != [str(n) for n in range(1, count + 1)]:
            _fail(source, node, 'macro_parameter_order', 'Structural macro must preserve each argument once in order')
        _validate_layout_body(source, definition.children)
        i = j + 1
    # Structural layout bodies are a supported-template assumption, not a TeX VM.


class TextReader:
    def __init__(self, source):
        self.source = source

    def fragment(self, start, end):
        raw = self.source.raw[start:end]
        local = SourceSnapshot(self.source.path, raw)
        try:
            return self._read(local, scan_latex(local))
        except LatexSyntaxError as error:
            a = start + error.span['start_byte']
            b = start + error.span['end_byte']
            raise LatexSyntaxError(error.code, 'Unsupported or malformed visible LaTeX', self.source,
                                   self.source.character_offset(a), self.source.character_offset(b)) from None

    def _read(self, source, nodes):
        output = []
        i = 0
        math = None
        skip_spaces = False
        while i < len(nodes):
            node = nodes[i]
            kind = node.kind
            if kind == 'comment':
                skip_spaces = True
                i += 1
                continue
            if kind == 'whitespace':
                if not skip_spaces:
                    output.append(' ')
                i += 1
                continue
            skip_spaces = False
            if kind == 'group':
                output.append(self._read(source, node.children))
            elif kind == 'text':
                text = node.raw(source)
                if any(c in text for c in '&_^#'):
                    _fail(source, node, 'unsupported_literal', 'Unescaped special character or unsupported math syntax')
                if math is None:
                    text = text.replace('---', '—').replace('--', '–').replace('``', '“').replace("''", '”').replace('~', ' ')
                output.append(text)
            elif kind == 'math_delimiter':
                if math is None:
                    math = node.name
                elif math == node.name:
                    math = None
                else:
                    _fail(source, node, 'math_mismatch', 'Mismatched math delimiters')
            elif kind == 'control_symbol':
                if node.name == '\\':
                    output.append('\n')
                elif node.name in '%&_{}$#':
                    output.append(node.name)
                elif node.name in {' ', '\t', '\n', '\r', '\r\n', ',', ';', ':'}:
                    output.append(' ')
                elif node.name == '!':
                    pass
                else:
                    _fail(source, node, 'unsupported_escape', 'Unsupported escaped character')
            elif kind == 'command':
                name = node.name
                if name in STYLES | {'resumeLine'}:
                    args, i = _arguments(source, nodes, i, 1)
                    output.append(self._read(source, args[0].children))
                    continue
                if name == 'href':
                    args, i = _arguments(source, nodes, i, 2)
                    output.append(self._read(source, args[1].children))
                    continue
                if name == 'url':
                    args, i = _arguments(source, nodes, i, 1)
                    # Dashes and tildes in URLs are literal, not typography.
                    literal = _body(source, args[0])
                    if '%' in literal or '\\' in literal or '{' in literal or '}' in literal:
                        _fail(source, node, 'unsupported_url', 'Complex URL syntax is unsupported')
                    output.append(literal)
                    continue
                if name in {'begin', 'end'}:
                    args, i = _arguments(source, nodes, i, 1)
                    if _body(source, args[0]) not in {'center', 'itemize', 'enumerate'}:
                        _fail(source, node, 'unsupported_environment', 'Unsupported visible environment')
                    # enumitem list options are layout metadata; retain no text.
                    if name == 'begin' and i < len(nodes) and nodes[i].raw(source).startswith('['):
                        while i < len(nodes) and ']' not in nodes[i].raw(source):
                            i += 1
                        if i == len(nodes) or not nodes[i].raw(source).endswith(']'):
                            _fail(source, node, 'unsupported_options', 'Unsupported environment options')
                        i += 1
                    continue
                if name in {'vspace', 'hspace'}:
                    args, i = _arguments(source, nodes, i, 1)
                    continue
                if name in DECLARATIONS:
                    skip_spaces = True
                elif name in SYMBOLS:
                    output.append(SYMBOLS[name])
                    skip_spaces = True
                elif name in {'item', 'par', 'newline'}:
                    if name == 'item' and i + 1 < len(nodes) and nodes[i + 1].raw(source).startswith('['):
                        _fail(source, node, 'unsupported_item_label', 'Optional item labels are unsupported')
                    output.append('\n')
                    skip_spaces = True
                elif name in {'hfill', 'quad', 'qquad'}:
                    output.append(' ')
                    skip_spaces = True
                else:
                    _fail(source, node, 'unsupported_command', 'Unsupported visible command')
            i += 1
        if math is not None:
            anchor = nodes[-1]
            _fail(source, anchor, 'unclosed_math', 'Unclosed math delimiter')
        return ''.join(output)

    def text(self, span, single_line=True):
        value = self.fragment(span['start_byte'], span['end_byte'])
        if single_line:
            return ' '.join(value.split())
        return '\n'.join(' '.join(line.split()) for line in value.split('\n') if line.strip())

    def raw_lines(self, item):
        """Split top-level explicit line breaks; preserve wrapper ranges."""
        start = item['span']['start_byte']
        local = SourceSnapshot(self.source.path, item['raw_latex'].encode())
        nodes = scan_latex(local)
        chunks, chunk = [], []
        for n in nodes:
            if n.kind == 'control_symbol' and n.name == '\\':
                chunks.append(chunk)
                chunk = []
            else:
                chunk.append(n)
        chunks.append(chunk)
        result = []
        for chunk in chunks:
            meaningful = [n for n in chunk if n.kind not in {'whitespace', 'comment'}]
            if not meaningful:
                continue
            a, b = start + meaningful[0].start_byte, start + meaningful[-1].end_byte
            span = self.source.span(a, b)
            text = self.text(span, single_line=False)
            if text:
                result.append({'kind': 'text', 'span': span,
                               'raw_latex': self.source.slice_text(a, b), 'text': text})
        return result


def readable_text(record):
    def entry_lines(entry):
        lines = [entry['heading']['text']]
        for item in entry['items']:
            if item['kind'] == 'entry':
                lines.extend(['', *entry_lines(item)])
            elif item['kind'] == 'bullet':
                lines.append('•' + (' ' + item['text'] if item['text'] else ''))
            else:
                lines.append(item['text'])
        return lines
    blocks = []
    if record['header']:
        blocks.append('\n'.join(item['text'] for item in record['header']))
    for section in record['sections']:
        parts = [section['title']['text'].upper()]
        previous_entry = False
        for item in section['items']:
            is_entry = item['kind'] == 'entry'
            if len(parts) == 1 or previous_entry or is_entry:
                parts.append('')
            parts.extend(entry_lines(item) if is_entry else [item['text']])
            previous_entry = is_entry
        blocks.append('\n'.join(parts))
    return '\n\n'.join(blocks).rstrip() + ('\n' if blocks else '')


def parse_cv(source: SourceSnapshot):
    _validate_definitions(source)
    structure = extract_structure(source)
    reader = TextReader(source)

    def items(values, owner):
        result = []
        lines = 0
        for original in values:
            value = deepcopy(original)
            kind = value['kind']
            if kind == 'raw':
                for line in reader.raw_lines(value):
                    lines += 1
                    line['id'] = f'h{lines}' if owner == 'header' else f'{owner}.line{lines}'
                    result.append(line)
            elif kind == 'entry':
                h = value['heading']
                for f in h['fields']:
                    f['text'] = reader.text(f['span'])
                row_size = 2
                h['text'] = '\n'.join(' '.join(f['text'] for f in h['fields'][i:i + row_size] if f['text'])
                                      for i in range(0, len(h['fields']), row_size))
                value['items'] = items(value['items'], value['id'])
                end = value['items'][-1]['span']['end_byte'] if value['items'] else h['span']['end_byte']
                value['span'] = source.span(value['span']['start_byte'], end)
                result.append(value)
            else:
                if kind == 'text':
                    lines += 1
                    value['id'] = f'{owner}.line{lines}'
                value['text'] = reader.text(value['body_span'] if kind == 'bullet' else value['span'])
                result.append(value)
        return result

    sections = deepcopy(list(structure.sections))
    for section in sections:
        section['title']['text'] = reader.text(section['title']['span'])
        section['items'] = items(section['items'], section['id'])
    record = {'schema_version': SCHEMA_VERSION, 'parser_version': PARSER_VERSION,
              'source_path': str(source.path), 'source_sha256': source.sha256,
              'header': items(structure.header, 'header'), 'sections': sections,
              'diagnostics': []}
    record['readable_text'] = readable_text(record)
    return record
