"""Immutable UTF-8 source snapshots and locations; no LaTeX interpretation."""

from bisect import bisect_left, bisect_right
from dataclasses import dataclass, field
import hashlib
from pathlib import Path
import re


class SourceEncodingError(ValueError):
    """The source cannot be decoded without losing original bytes."""

    code = "invalid_utf8"

    def __init__(self, path: Path, start: int, end: int):
        self.path = path
        self.start_byte = start
        self.end_byte = end
        super().__init__(f"Invalid UTF-8 in {path} at byte range [{start}, {end}).")


@dataclass(frozen=True)
class SourceSnapshot:
    """One exact file revision. All offsets are relative to this snapshot.

    Character offsets index Python's decoded string; byte offsets index raw.
    Position columns count code points, including tabs and combining marks.
    """

    path: Path
    raw: bytes = field(repr=False)
    text: str = field(init=False, repr=False)
    sha256: str = field(init=False)
    _byte_offsets: tuple[int, ...] = field(init=False, repr=False)
    _line_starts: tuple[int, ...] = field(init=False, repr=False)

    def __post_init__(self):
        path = Path(self.path).resolve()
        if not isinstance(self.raw, bytes):
            raise TypeError("SourceSnapshot requires immutable bytes")
        try:
            text = self.raw.decode("utf-8")
        except UnicodeDecodeError as error:
            raise SourceEncodingError(path, error.start, error.end) from None
        offsets = [0]
        for char in text:
            offsets.append(offsets[-1] + len(char.encode("utf-8")))
        starts = [0] + [match.end() for match in re.finditer(r"\r\n|\r|\n", text)]
        object.__setattr__(self, "path", path)
        object.__setattr__(self, "text", text)
        object.__setattr__(self, "sha256", hashlib.sha256(self.raw).hexdigest())
        object.__setattr__(self, "_byte_offsets", tuple(offsets))
        object.__setattr__(self, "_line_starts", tuple(starts))

    @classmethod
    def read(cls, path: str | Path) -> "SourceSnapshot":
        """Read once in binary mode. OS errors propagate; never use stale data."""
        resolved = Path(path).resolve()
        return cls(resolved, resolved.read_bytes())

    @staticmethod
    def _check_offset(offset: int, maximum: int) -> None:
        if type(offset) is not int:
            raise TypeError("Offsets must be integers")
        if not 0 <= offset <= maximum:
            raise ValueError(f"Offset {offset} is outside [0, {maximum}]")

    def byte_offset(self, character_offset: int) -> int:
        """Convert a decoded-text boundary to an original-byte boundary."""
        self._check_offset(character_offset, len(self.text))
        return self._byte_offsets[character_offset]

    def character_offset(self, byte_offset: int) -> int:
        """Reject offsets inside a UTF-8 encoded character."""
        self._check_offset(byte_offset, len(self.raw))
        index = bisect_left(self._byte_offsets, byte_offset)
        if self._byte_offsets[index] != byte_offset:
            raise ValueError(f"Byte offset {byte_offset} splits a UTF-8 character")
        return index

    def position(self, byte_offset: int) -> dict[str, int]:
        """Return one-based line/column at a validated original-byte boundary."""
        character = self.character_offset(byte_offset)
        line_index = bisect_right(self._line_starts, character) - 1
        return {"line": line_index + 1,
                "column": character - self._line_starts[line_index] + 1}

    def span(self, start_byte: int, end_byte: int) -> dict:
        """Return a JSON-ready half-open span, including empty and EOF spans."""
        start = self.position(start_byte)
        end = self.position(end_byte)
        if start_byte > end_byte:
            raise ValueError("Span start must not exceed its end")
        return {"start_byte": start_byte, "end_byte": end_byte,
                "start": start, "end": end}

    def span_from_characters(self, start: int, end: int) -> dict:
        """Convert scanner/string offsets without mixing bytes and characters."""
        return self.span(self.byte_offset(start), self.byte_offset(end))

    def slice_text(self, start_byte: int, end_byte: int) -> str:
        """Extract exact source text without newline or Unicode normalisation."""
        self.span(start_byte, end_byte)
        return self.raw[start_byte:end_byte].decode("utf-8")
