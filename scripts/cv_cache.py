"""Private, disposable cache for complete read-only CV extraction."""
from dataclasses import dataclass
import hashlib
import json
import os
from pathlib import Path
import tempfile

from scripts import cv_text
from scripts.cv_source import SourceSnapshot


class SourceChangedError(ValueError):
    pass


@dataclass(frozen=True)
class CacheResult:
    record: dict
    status: str
    warnings: tuple[str, ...] = ()


def _canonical(record):
    return json.dumps(record, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode('utf-8')


def _validate(record, source):
    """Validate types, source slices and containment without re-running parsing."""
    if not isinstance(record, dict):
        return False
    if record.get('schema_version') != cv_text.SCHEMA_VERSION or type(record.get('schema_version')) is not int:
        return False
    if record.get('parser_version') != cv_text.PARSER_VERSION:
        return False
    if record.get('source_path') != str(source.path) or record.get('source_sha256') != source.sha256:
        return False
    if record.get('diagnostics') != [] or not isinstance(record.get('readable_text'), str):
        return False
    ids = set()

    def span(value):
        if not isinstance(value, dict):
            raise ValueError('Invalid span')
        a, b = value['start_byte'], value['end_byte']
        if value != source.span(a, b):
            raise ValueError('Invalid location')
        return a, b

    def nodes(values, allowed, parent=None):
        if not isinstance(values, list):
            raise ValueError('Invalid node list')
        previous = -1
        for node in values:
            if not isinstance(node, dict) or node.get('kind') not in allowed:
                raise ValueError('Invalid node')
            id = node['id']
            if not isinstance(id, str) or not id or id in ids:
                raise ValueError('Invalid ID')
            ids.add(id)
            a, b = span(node['span'])
            if a < previous or (parent and not parent[0] <= a <= b <= parent[1]):
                raise ValueError('Invalid containment/order')
            previous = b
            kind = node['kind']
            if kind in {'text', 'field', 'heading', 'bullet'}:
                if not isinstance(node['text'], str) or node['raw_latex'] != source.slice_text(a, b):
                    raise ValueError('Invalid content')
            if kind == 'section':
                nodes([node['title']], {'field'}, (a, b))
                nodes(node['items'], {'entry', 'text'}, (a, b))
            elif kind == 'entry':
                nodes([node['heading']], {'heading'}, (a, b))
                nodes(node['items'], {'entry', 'text', 'bullet'}, (a, b))
            elif kind == 'heading':
                command = node['command']
                if command not in cv_text.HEADINGS or len(node['fields']) != cv_text.HEADINGS[command]:
                    raise ValueError('Invalid heading')
                nodes(node['fields'], {'field'}, (a, b))
                if [f.get('argument_index') for f in node['fields']] != list(range(1, len(node['fields']) + 1)):
                    raise ValueError('Invalid heading arguments')
            elif kind == 'bullet':
                c, d = span(node['body_span'])
                if not a <= c <= d <= b or node['body_latex'] != source.slice_text(c, d) or node['command'] != 'resumeItem':
                    raise ValueError('Invalid bullet body')
    try:
        nodes(record['header'], {'text'})
        nodes(record['sections'], {'section'})
        return record['readable_text'] == cv_text.readable_text(record)
    except (KeyError, ValueError, TypeError, IndexError, RecursionError):
        return False


def _cache_paths(source):
    # Do not create caches next to arbitrary files or inside tracked fixture paths.
    if source.path.parent.name != 'workspace' or source.path.name not in {'main.tex', 'tailored.tex'}:
        raise ValueError('Caching requires workspace/main.tex or workspace/tailored.tex; use --no-cache for other files')
    cache = source.path.parent / '.cache'
    directory = cache / 'cv'
    for path in (cache, directory):
        if path.is_symlink():
            raise ValueError('Cache directories must not be symbolic links')
    paths = (directory / (source.path.stem + '.json'), directory / (source.path.stem + '.txt'))
    if any(p.is_symlink() for p in paths):
        raise ValueError('Cache files must not be symbolic links')
    return paths


def _atomic_write(path, content):
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    fd, temporary = tempfile.mkstemp(prefix='.' + path.name + '-', dir=path.parent)
    try:
        with os.fdopen(fd, 'wb') as stream:
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        try:
            os.unlink(temporary)
        except FileNotFoundError:
            pass


def _assert_current(source):
    if hashlib.sha256(source.path.read_bytes()).hexdigest() != source.sha256:
        raise SourceChangedError('Source changed during extraction; retry with the current file')


def load_cv(path, *, use_cache=True):
    """Always read current source. Return current in-memory data, never stale views."""
    source = SourceSnapshot.read(path)
    if not use_cache:
        record = cv_text.parse_cv(source)
        _assert_current(source)
        return CacheResult(record, 'disabled')
    json_path, text_path = _cache_paths(source)
    record = None
    try:
        stored = json.loads(json_path.read_text(encoding='utf-8'))
        checksum = stored.pop('cache_sha256')
        if checksum == hashlib.sha256(_canonical(stored)).hexdigest() and _validate(stored, source):
            record = stored
    except (OSError, ValueError, KeyError, TypeError, AttributeError, RecursionError):
        pass
    hit = record is not None
    if not hit:
        record = cv_text.parse_cv(source)
        if not _validate(record, source):
            raise ValueError('Parser output does not satisfy the cache contract')
    _assert_current(source)
    warnings = []
    try:
        if not hit:
            stored = dict(record, cache_sha256=hashlib.sha256(_canonical(record)).hexdigest())
            _atomic_write(json_path, (json.dumps(stored, ensure_ascii=False, indent=2) + '\n').encode())
        expected = record['readable_text'].encode('utf-8')
        try:
            current = text_path.read_bytes()
        except OSError:
            current = None
        if current != expected:
            _atomic_write(text_path, expected)
    except OSError:
        warnings.append('Cache could not be fully written; using current in-memory extraction, not the on-disk text view')
    _assert_current(source)
    return CacheResult(record, 'hit' if hit else 'rebuilt', tuple(warnings))
