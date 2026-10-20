"""Read-only CLI: inspect a CV or list its uniquely identified entries."""
import argparse
import json
from pathlib import Path
import sys

# Support direct invocation by absolute path from any working directory.
if __package__ in {None, ''}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.cv_cache import load_cv, SourceChangedError
from scripts.cv_latex import LatexSyntaxError
from scripts.cv_source import SourceEncodingError


def list_entries(record):
    entries = []
    def visit(items, section, parent=None):
        for item in items:
            if item['kind'] != 'entry':
                continue
            bullets = [b for b in item['items'] if b['kind'] == 'bullet']
            entries.append({'id': item['id'], 'section_id': section['id'],
                            'section': section['title']['text'], 'parent_id': parent,
                            'heading': item['heading']['text'],
                            'bullet_count': len(bullets),
                            'empty_bullet_count': sum(not b['text'] for b in bullets),
                            'line': item['span']['start']['line']})
            visit(item['items'], section, item['id'])
    for section in record['sections']:
        visit(section['items'], section)
    return entries


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    default = Path(__file__).resolve().parents[1] / 'workspace/main.tex'
    for name in ('inspect', 'list'):
        command = commands.add_parser(name)
        command.add_argument('source', nargs='?', type=Path, default=default,
                             help='CV path (default: this checkout/workspace/main.tex)')
        command.add_argument('--json', action='store_true', help='Print structured JSON')
        command.add_argument('--no-cache', action='store_true', help='Do not read or write a cache')
    args = parser.parse_args(argv)
    try:
        result = load_cv(args.source, use_cache=not args.no_cache)
    except (LatexSyntaxError, SourceEncodingError, SourceChangedError, OSError, ValueError) as error:
        diagnostic = {'code': getattr(error, 'code', 'source_changed' if isinstance(error, SourceChangedError) else 'parser_error'),
                      'severity': 'error', 'message': str(error), 'span': getattr(error, 'span', None)}
        print(json.dumps(diagnostic, ensure_ascii=False), file=sys.stderr)
        return 1
    for warning in result.warnings:
        print(json.dumps({'code': 'cache_write_failed', 'severity': 'warning', 'message': warning}), file=sys.stderr)
    if args.command == 'inspect':
        if args.json:
            print(json.dumps(result.record, ensure_ascii=False, indent=2))
        else:
            print(result.record['readable_text'], end='')
    else:
        entries = list_entries(result.record)
        if args.json:
            print(json.dumps({'source_path': result.record['source_path'],
                              'source_sha256': result.record['source_sha256'],
                              'entries': entries}, ensure_ascii=False, indent=2))
        else:
            for entry in entries:
                heading = entry['heading'].replace('\n', ' | ')
                print(f"{entry['id']}\t{entry['section']}\t{heading}\t"
                      f"{entry['bullet_count']} bullets ({entry['empty_bullet_count']} empty)\tline {entry['line']}")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
