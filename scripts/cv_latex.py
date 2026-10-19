"""Lossless structural scanning for the supported LaTeX CV syntax.

This layer records syntax, not macro expansion, argument ownership or visible text.
"""
from dataclasses import dataclass

from scripts.cv_source import SourceSnapshot


class LatexSyntaxError(ValueError):
    """A located syntax error; messages do not include private source content."""

    def __init__(self, code, message, source, start, end):
        self.code = code
        self.span = source.span_from_characters(start, end)
        self.path = source.path
        position = self.span['start']
        super().__init__(f"{message} ({source.path}:{position['line']}:{position['column']})")


@dataclass(frozen=True)
class LatexNode:
    kind: str
    start_byte: int
    end_byte: int
    name: str | None = None
    children: tuple['LatexNode', ...] = ()
    body_start_byte: int | None = None
    body_end_byte: int | None = None

    def raw(self, source: SourceSnapshot) -> str:
        return source.slice_text(self.start_byte, self.end_byte)

    def span(self, source: SourceSnapshot) -> dict:
        return source.span(self.start_byte, self.end_byte)

    def body_span(self, source: SourceSnapshot) -> dict | None:
        if self.kind != 'group':
            return None
        return source.span(self.body_start_byte, self.body_end_byte)


def scan_latex(source: SourceSnapshot, *, max_depth: int = 128) -> tuple[LatexNode, ...]:
    """Scan a snapshot into nested, ordered nodes without dropping any bytes.

    Commands and their following groups are siblings. The caller decides which
    groups are arguments using known command signatures. Square brackets and
    stars remain text. Escapes are control-symbol nodes, never group delimiters.
    An explicit stack avoids Python recursion limits on malformed/deep input.
    """
    if type(max_depth) is not int or max_depth < 1:
        raise ValueError('max_depth must be a positive integer')
    text = source.text
    root = []
    current = root
    stack = []
    i = 0

    def node(kind, start, end, **kwargs):
        return LatexNode(kind, source.byte_offset(start), source.byte_offset(end), **kwargs)

    while i < len(text):
        start = i
        char = text[i]
        if char == '{':
            if len(stack) >= max_depth:
                raise LatexSyntaxError('nesting_limit', 'LaTeX group nesting limit exceeded', source, i, i + 1)
            stack.append((i, current))
            current = []
            i += 1
        elif char == '}':
            if not stack:
                raise LatexSyntaxError('unexpected_close_brace', 'Unexpected closing brace', source, i, i + 1)
            opening, parent = stack.pop()
            parent.append(node('group', opening, i + 1, children=tuple(current),
                               body_start_byte=source.byte_offset(opening + 1),
                               body_end_byte=source.byte_offset(i)))
            current = parent
            i += 1
        elif char == '%':
            i += 1
            while i < len(text) and text[i] not in '\r\n':
                i += 1
            if i < len(text):
                i += 2 if text[i:i + 2] == '\r\n' else 1
            current.append(node('comment', start, i))
        elif char == '\\':
            i += 1
            if i == len(text):
                raise LatexSyntaxError('incomplete_command', 'Trailing backslash without a command', source, start, i)
            if text[i].isascii() and text[i].isalpha():
                while i < len(text) and text[i].isascii() and text[i].isalpha():
                    i += 1
                name = text[start + 1:i]
                if name in {'verb', 'catcode', 'makeatletter', 'ExplSyntaxOn'}:
                    raise LatexSyntaxError('unsupported_lexical_command',
                                           'Command changes or bypasses supported lexical rules', source, start, i)
                current.append(node('command', start, i, name=name))
            else:
                # A backslash followed by a physical newline is a control space.
                i += 2 if text[i:i + 2] == '\r\n' else 1
                current.append(node('control_symbol', start, i, name=text[start + 1:i]))
        elif char in ' \t\r\n':
            i += 1
            while i < len(text) and text[i] in ' \t\r\n':
                i += 1
            current.append(node('whitespace', start, i))
        elif char == '$':
            i += 2 if text[i:i + 2] == '$$' else 1
            current.append(node('math_delimiter', start, i, name=text[start:i]))
        else:
            i += 1
            while i < len(text) and text[i] not in '{}%\\$ \t\r\n':
                i += 1
            current.append(node('text', start, i))
    if stack:
        opening, _ = stack[-1]
        raise LatexSyntaxError('unclosed_group', 'Unclosed brace group', source, opening, opening + 1)
    return tuple(root)
