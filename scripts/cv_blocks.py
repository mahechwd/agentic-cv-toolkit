#!/usr/bin/env python3
"""Inspect named CV blocks and enforce visible bullet limits."""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

from cv_tex import mask_comments, parse_braced, rendered_text


HEADING_PATTERN = re.compile(r"\\(resumeSubheading|resumeProjectHeading)\b")


@dataclass(frozen=True)
class BulletSpan:
    content_start: int
    content_end: int
    latex: str
    rendered: str
    characters: int
    line: int


@dataclass(frozen=True)
class CvTarget:
    kind: str
    name: str
    context: str
    start: int
    end: int
    bullets: tuple[BulletSpan, ...]


@dataclass(frozen=True)
class TargetLengthCheck:
    kind: str
    name: str
    bullet_characters: tuple[int, ...]
    average_characters: float
    max_characters: int
    max_average: float
    violations: tuple[str, ...]

    @property
    def passed(self) -> bool:
        return not self.violations


def read_utf8(path: Path) -> str:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return handle.read()


def _skip_space(source: str, cursor: int) -> int:
    while cursor < len(source) and source[cursor].isspace():
        cursor += 1
    return cursor


def _command_arguments(
    original: str,
    masked: str,
    command_end: int,
    count: int,
) -> tuple[list[str], int]:
    arguments: list[str] = []
    cursor = command_end
    for _ in range(count):
        cursor = _skip_space(masked, cursor)
        if cursor >= len(masked) or masked[cursor] != "{":
            raise ValueError(f"expected braced command argument near character {cursor}")
        _, next_cursor = parse_braced(masked, cursor)
        arguments.append(original[cursor + 1 : next_cursor - 1])
        cursor = next_cursor
    return arguments, cursor


def _normalise_name(value: str) -> str:
    return re.sub(r"[\W_]+", " ", value.casefold()).strip()


def _project_name(raw_heading: str) -> str:
    masked = mask_comments(raw_heading)
    match = re.search(r"\\textbf\s*\{", masked)
    if match:
        opening = masked.find("{", match.start())
        _, end = parse_braced(masked, opening)
        name = rendered_text(raw_heading[opening + 1 : end - 1])
    else:
        name = rendered_text(raw_heading).split("|", 1)[0].strip()
    if not name:
        raise ValueError("project heading has no readable project name")
    return name


def _next_boundary(masked: str, cursor: int) -> int:
    match = re.search(
        r"\\(?:resumeSubheading|resumeProjectHeading|section)\b",
        masked[cursor:],
    )
    return len(masked) if match is None else cursor + match.start()


def _extract_bullets(
    original: str,
    masked: str,
    start: int,
    end: int,
) -> tuple[tuple[BulletSpan, ...], int]:
    list_start_match = re.search(r"\\resumeItemListStart\b", masked[start:end])
    if list_start_match is None:
        raise ValueError("target heading has no immediately associated resume item list")
    list_start = start + list_start_match.end()
    list_end_match = re.search(r"\\resumeItemListEnd\b", masked[list_start:end])
    if list_end_match is None:
        raise ValueError("target resume item list has no end marker")
    list_end_start = list_start + list_end_match.start()
    block_end = list_start + list_end_match.end()

    nested_list = re.search(r"\\resumeItemListStart\b", masked[list_start:list_end_start])
    if nested_list is not None:
        raise ValueError("nested resume item lists are not supported")

    bullets: list[BulletSpan] = []
    cursor = list_start
    pattern = re.compile(r"\\resumeItem\s*\{")
    while match := pattern.search(masked, cursor, list_end_start):
        opening = masked.find("{", match.start(), match.end())
        _, next_cursor = parse_braced(masked, opening)
        if next_cursor > list_end_start:
            raise ValueError("resume item extends beyond its item list")
        latex = original[opening + 1 : next_cursor - 1]
        visible = rendered_text(latex)
        bullets.append(
            BulletSpan(
                content_start=opening + 1,
                content_end=next_cursor - 1,
                latex=latex,
                rendered=visible,
                characters=len(visible),
                line=original.count("\n", 0, match.start()) + 1,
            )
        )
        cursor = next_cursor
    return tuple(bullets), block_end


def scan_targets(cv_path: Path) -> list[CvTarget]:
    original = read_utf8(cv_path)
    masked = mask_comments(original)
    document_at = masked.find(r"\begin{document}")
    if document_at < 0:
        raise ValueError(f"{cv_path} does not contain \\begin{{document}}")

    targets: list[CvTarget] = []
    for match in HEADING_PATTERN.finditer(masked, document_at):
        command = match.group(1)
        argument_count = 4 if command == "resumeSubheading" else 2
        arguments, command_end = _command_arguments(
            original,
            masked,
            match.end(),
            argument_count,
        )
        boundary = _next_boundary(masked, command_end)
        try:
            bullets, block_end = _extract_bullets(
                original,
                masked,
                command_end,
                boundary,
            )
        except ValueError as error:
            if "no immediately associated" in str(error):
                continue
            raise

        if command == "resumeSubheading":
            kind = "experience"
            name = rendered_text(arguments[2])
            context = rendered_text(arguments[0])
        else:
            kind = "project"
            name = _project_name(arguments[0])
            rendered_heading = rendered_text(arguments[0])
            heading_parts = rendered_heading.split("|", 1)
            context = heading_parts[1].strip() if len(heading_parts) == 2 else ""
        if not name:
            raise ValueError(f"{command} near line {original.count(chr(10), 0, match.start()) + 1} has no name")
        targets.append(
            CvTarget(
                kind=kind,
                name=name,
                context=context,
                start=match.start(),
                end=block_end,
                bullets=bullets,
            )
        )
    return targets


def select_target(cv_path: Path, kind: str, name: str) -> CvTarget:
    canonical_kind = canonicalise_kind(kind)
    normalised_name = _normalise_name(name)
    matches = [
        target
        for target in scan_targets(cv_path)
        if target.kind == canonical_kind
        and _normalise_name(target.name) == normalised_name
    ]
    if not matches:
        available = ", ".join(
            f"{target.kind}:{target.name}" for target in scan_targets(cv_path)
        )
        raise ValueError(
            f"no exact {canonical_kind} target named {name!r}; available: {available or 'none'}"
        )
    if len(matches) > 1:
        raise ValueError(
            f"target {name!r} is ambiguous; use a CV with unique experience/project names"
        )
    return matches[0]


def canonicalise_kind(kind: str) -> str:
    normalised = kind.casefold().strip()
    if normalised in {"experience", "experiences"}:
        return "experience"
    if normalised in {"project", "projects"}:
        return "project"
    raise ValueError("kind must be experience or project")


def check_target_lengths(
    cv_path: Path,
    kind: str,
    target_name: str,
    max_characters: int = 220,
    max_average: float = 180,
) -> TargetLengthCheck:
    if max_characters < 1:
        raise ValueError("max characters must be a positive integer")
    if max_average <= 0:
        raise ValueError("max average must be positive")

    target = select_target(cv_path, kind, target_name)
    if not target.bullets:
        raise ValueError("target has no active resumeItem slots")

    counts = tuple(bullet.characters for bullet in target.bullets)
    average = sum(counts) / len(counts)
    violations: list[str] = []
    for index, bullet in enumerate(target.bullets, start=1):
        if not bullet.rendered:
            violations.append(f"bullet {index} is empty")
        if bullet.characters > max_characters:
            violations.append(
                f"bullet {index} is {bullet.characters} characters; "
                f"maximum is {max_characters}"
            )
    if average > max_average:
        violations.append(
            f"block average is {average:.1f} characters; maximum is {max_average:g}"
        )

    return TargetLengthCheck(
        kind=target.kind,
        name=target.name,
        bullet_characters=counts,
        average_characters=average,
        max_characters=max_characters,
        max_average=max_average,
        violations=tuple(violations),
    )


def format_target_length_check(check: TargetLengthCheck) -> str:
    lines = [f"target: {check.kind}:{check.name}"]
    lines.extend(
        f"bullet {index}: {characters} characters"
        for index, characters in enumerate(check.bullet_characters, start=1)
    )
    lines.append(
        f"average: {check.average_characters:.1f} characters "
        f"(maximum {check.max_average:g})"
    )
    lines.append(
        f"per-bullet maximum: {check.max_characters} characters"
    )
    lines.append(f"result: {'PASS' if check.passed else 'FAIL'}")
    lines.extend(f"- {violation}" for violation in check.violations)
    return "\n".join(lines)


def _target_payload(target: CvTarget) -> dict[str, object]:
    return {
        "kind": target.kind,
        "name": target.name,
        "context": target.context,
        "bullet_count": len(target.bullets),
        "bullets": [asdict(bullet) for bullet in target.bullets],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)

    list_parser = subparsers.add_parser("list", help="List editable CV targets")
    list_parser.add_argument("cv", type=Path)
    list_parser.add_argument("--json", action="store_true")

    check_parser = subparsers.add_parser(
        "check",
        help="Check one target's visible bullet lengths",
    )
    check_parser.add_argument("--cv", type=Path, required=True)
    check_parser.add_argument("--kind", required=True)
    check_parser.add_argument("--target", required=True)
    check_parser.add_argument("--max-chars", type=int, default=220)
    check_parser.add_argument("--max-average", type=float, default=180)

    args = parser.parse_args()
    try:
        if args.command == "list":
            targets = scan_targets(args.cv)
            if args.json:
                print(json.dumps([_target_payload(target) for target in targets], indent=2))
            else:
                for target in targets:
                    context = f" — {target.context}" if target.context else ""
                    print(f"{target.kind}: {target.name}{context} ({len(target.bullets)} bullets)")
        elif args.command == "check":
            check = check_target_lengths(
                args.cv,
                args.kind,
                args.target,
                args.max_chars,
                args.max_average,
            )
            print(format_target_length_check(check))
            if not check.passed:
                return 4
    except (OSError, ValueError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
