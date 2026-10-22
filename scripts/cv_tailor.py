"""Private tailoring preparation and publication; language decisions belong to the skill."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import sys
import tempfile

if __package__ in {None, ''}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts.cv_source import SourceSnapshot
from scripts.cv_text import parse_cv

PREFIX = b'% cv-tailor-state: '


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def jd_hash(raw):
    text = ' '.join(raw.decode('utf-8').split())
    if not text:
        raise ValueError('job-description.txt is empty; supply the JD first')
    return digest(text.encode())


def unpack(raw):
    if not raw.strip():
        return raw, None
    line, separator, body = raw.partition(b'\n')
    if not line.startswith(PREFIX):
        raise ValueError('Existing tailored.tex has no JD state; report this before proceeding')
    try:
        state = json.loads(line[len(PREFIX):])
        if (state['version'] != 1 or state['content_sha256'] != digest(body)
                or not re.fullmatch('[0-9a-f]{64}', state['jd_sha256'])):
            raise ValueError()
    except (ValueError, KeyError, TypeError):
        raise ValueError('Existing tailored.tex has inconsistent JD state or was edited; report before proceeding') from None
    return body, state


def pack(body, jd):
    state = {'version': 1, 'jd_sha256': jd, 'content_sha256': digest(body)}
    return PREFIX + json.dumps(state, sort_keys=True).encode() + b'\n' + body


def record(raw):
    return parse_cv(SourceSnapshot(Path('/synthetic/candidate.tex'), raw))


def entries(cv):
    result = []
    def visit(items, section, ancestors=()):
        for item in items:
            if item['kind'] == 'entry':
                # Full heading fields plus ancestry, never snapshot-local IDs across files.
                identity = (section, *ancestors, tuple(f['text'] for f in item['heading']['fields']))
                result.append((identity, item))
                visit(item['items'], section, (*ancestors, identity[-1]))
    for section in cv['sections']:
        visit(section['items'], section['title']['text'])
    return result


def bullets(entry):
    return [x for x in entry['items'] if x['kind'] == 'bullet']


def resolve(cv, targets):
    if not targets:
        raise ValueError('Specify targets, e.g. an entry name or section:Experience')
    available = entries(cv)
    chosen = set()
    for target in targets:
        if target.startswith('section:'):
            name = target[8:]
            sections = [s for s in cv['sections'] if s['title']['text'] == name]
            if len(sections) != 1:
                raise ValueError(f'Missing or ambiguous section: {name}')
            matches = [(k, e) for k, e in available if k[0] == name]
        else:
            matches = [(k, e) for k, e in available if target == e['id'] or
                       target in [f['text'] for f in e['heading']['fields']]]
            if len(matches) != 1:
                raise ValueError(f'Missing or ambiguous entry: {target}; use parser list to disambiguate')
            parent = matches[0][1]
            matches = [(k, e) for k, e in available if
                       parent['span']['start_byte'] <= e['span']['start_byte'] and
                       e['span']['end_byte'] <= parent['span']['end_byte']]
        if not matches:
            raise ValueError(f'Target contains no entries: {target}')
        chosen.update(e['id'] for _, e in matches)
    selected = [(k, e) for k, e in available if e['id'] in chosen and bullets(e)]
    if not selected:
        raise ValueError('Selected targets contain no bullet slots')
    for _, entry in selected:
        if any(not b['text'].strip() for b in bullets(entry)):
            raise ValueError(f"Empty bullet slot in {entry['heading']['text']}; use cv-build first")
    return selected


def preflight(workspace, targets):
    workspace = Path(workspace).resolve()
    paths = [workspace / n for n in ('job-description.txt', 'tailored.tex', 'main.tex')]
    if any(p.is_symlink() for p in paths):
        raise ValueError('Workspace inputs must be regular files, not symlinks')
    # JD and saved-state validation deliberately precede CV parsing/target selection.
    jd_raw = paths[0].read_bytes()
    jd = jd_hash(jd_raw)
    destination = paths[1].read_bytes() if paths[1].exists() else b''
    old, state = unpack(destination)
    main = paths[2].read_bytes()
    if not main.strip():
        raise ValueError('main.tex is empty')
    cv = record(main)
    selected = resolve(cv, targets)
    reset = state is not None and state['jd_sha256'] != jd
    return {'workspace': str(workspace), 'targets': targets, 'jd_sha256': jd,
            'input_hashes': {'job-description.txt': digest(jd_raw), 'main.tex': digest(main),
                             'tailored.tex': digest(destination) if paths[1].exists() else None},
            'reset': reset, 'main': main, 'base': main if reset or not old.strip() else old,
            'selected': selected}


def replace(raw, edits):
    previous = len(raw)
    for start, end, body in sorted(edits, reverse=True):
        if not 0 <= start <= end <= previous:
            raise ValueError('Overlapping or invalid edit spans')
        raw = raw[:start] + body + raw[end:]
        previous = start
    return raw


def validate_body(body):
    """Restricted authored text + styles; existing untouched source is parser-validated."""
    if not isinstance(body, str) or not body.strip():
        raise ValueError('Bullet body must be non-empty text')
    depth = 0
    i = 0
    allowed = {'textbf', 'textit', 'emph', 'underline', 'textrm', 'textnormal', 'textsf', 'texttt',
               'textasciitilde', 'textasciicircum', 'textbackslash', 'LaTeX', 'TeX'}
    while i < len(body):
        char = body[i]
        if char == '\\':
            match = re.match(r'\\([A-Za-z]+|[%&#_${}])', body[i:])
            if not match or (match[1].isalpha() and match[1] not in allowed):
                raise ValueError('Unsupported command in generated bullet')
            i += len(match[0])
            continue
        if char in '%&#$^_~' or (ord(char) < 32 and char not in '\n\t'):
            raise ValueError('Escape special LaTeX characters in generated text')
        depth += (char == '{') - (char == '}')
        if depth < 0:
            raise ValueError('Unbalanced bullet braces')
        i += 1
    if depth:
        raise ValueError('Unbalanced bullet braces')


def candidate(plan, replacements):
    selected = plan['selected']
    expected = {b['id'] for _, e in selected for b in bullets(e)}
    if set(replacements) != expected:
        raise ValueError('Provide exactly every selected canonical bullet ID, including unchanged bullets')
    main_edits = []
    for _, entry in selected:
        for b in bullets(entry):
            body = replacements[b['id']]
            if body != b['body_latex']:
                validate_body(body)
            span = b['body_span']
            main_edits.append((span['start_byte'], span['end_byte'], body.encode()))
    authored = replace(plan['main'], main_edits)
    source_entries = dict(entries(record(authored)))
    destination_entries = entries(record(plan['base']))
    edits = []
    for identity, original in selected:
        matches = [e for key, e in destination_entries if key == identity]
        if len(matches) != 1 or sum(key == identity for key, _ in entries(record(authored))) != 1:
            raise ValueError('Cannot reliably match selected entry across files; report structure mismatch')
        src, dst = source_entries[identity], matches[0]
        sb, db = bullets(src), bullets(dst)
        if len(sb) == len(db):
            for a, b in zip(sb, db):
                span = b['body_span']
                edits.append((span['start_byte'], span['end_byte'], a['body_latex'].encode()))
        else:
            # Refresh the canonical direct bullet run automatically, including added/removed slots.
            if not db:
                raise ValueError('Destination has no bullet run to synchronise safely')
            for entry, bs in ((src, sb), (dst, db)):
                lo, hi = bs[0]['span']['start_byte'], bs[-1]['span']['end_byte']
                if any(x['kind'] != 'bullet' and lo <= x['span']['start_byte'] < hi for x in entry['items']):
                    raise ValueError('Cannot synchronise an interleaved bullet run safely')
            edits.append((db[0]['span']['start_byte'], db[-1]['span']['end_byte'],
                          authored[sb[0]['span']['start_byte']:sb[-1]['span']['end_byte']]))
    result = replace(plan['base'], edits)
    verified = record(result)
    actual = dict(entries(verified))
    for identity, _ in selected:
        if [b['body_latex'] for b in bullets(actual[identity])] != [b['body_latex'] for b in bullets(source_entries[identity])]:
            raise ValueError('Candidate does not preserve selected canonical slots')
    return pack(result, plan['jd_sha256'])


def atomic_write(path, raw):
    fd, name = tempfile.mkstemp(prefix='.cv-tailor-', dir=path.parent)
    try:
        with os.fdopen(fd, 'wb') as stream:
            stream.write(raw)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(name, path)
    finally:
        if os.path.exists(name):
            os.unlink(name)


def prepare(workspace, targets, replacements, session=None):
    plan = preflight(workspace, targets)
    raw = candidate(plan, replacements)
    directory = Path(session) if session else Path(tempfile.mkdtemp(prefix='cv-tailor-'))
    if session:
        old = json.loads((directory / 'manifest.json').read_text())
        if old['input_hashes'] != plan['input_hashes'] or old['targets'] != targets:
            raise ValueError('Inputs or targets changed; start a new request')
        if old.get('failed_rounds', 0) >= 3:
            raise ValueError('Three failed verification rounds reached; stop this request')
    else:
        old = {}
    manifest = {k: v for k, v in plan.items() if k not in {'main', 'base', 'selected'}}
    manifest.update(candidate_sha256=digest(raw), failed_rounds=old.get('failed_rounds', 0),
                    replacements=replacements)
    atomic_write(directory / 'candidate.tex', raw)
    atomic_write(directory / 'manifest.json', json.dumps(manifest, indent=2).encode())
    return directory


def publish(session, review):
    directory = Path(session)
    manifest = json.loads((directory / 'manifest.json').read_text())
    workspace = Path(manifest['workspace'])
    # Serialise cooperating writers. Never overwrite a stale lock automatically.
    lock = workspace / '.cv-tailor.lock'
    fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    try:
        plan = preflight(workspace, manifest['targets'])
        if plan['input_hashes'] != manifest['input_hashes']:
            raise ValueError('Inputs changed during tailoring; destination preserved')
        raw = (directory / 'candidate.tex').read_bytes()
        if raw != candidate(plan, manifest['replacements']) or digest(raw) != manifest['candidate_sha256']:
            raise ValueError('Candidate changed after preparation')
        destination = workspace / 'tailored.tex'
        if destination.exists() and destination.read_bytes() == raw:
            return 'unchanged'
        compilation = json.loads((directory / 'compilation.json').read_text())
        pdf = directory / 'candidate.pdf'
        if (compilation['candidate_sha256'] != digest(raw) or
                compilation['pdf_sha256'] != digest(pdf.read_bytes())):
            raise ValueError('Compilation is stale')
        if review.get('candidate_sha256') != digest(raw) or review.get('pdf_sha256') != compilation['pdf_sha256']:
            raise ValueError('Review is stale')
        expected = set(manifest['replacements'])
        observations = review.get('bullets', {})
        passed = (set(observations) == expected and review.get('images_inspected') is True
                  and review.get('balanced') is True and all(
                      type(o.get('lines')) is int and 1 <= o['lines'] <= 2
                      and type(o.get('final_line_fill')) in (int, float)
                      and 0 < o['final_line_fill'] <= 1
                      and o.get('mapping_confident') is True
                      for o in observations.values()))
        if manifest['failed_rounds'] >= 3:
            raise ValueError('Three failed verification rounds reached')
        if not passed:
            manifest['failed_rounds'] += 1
            atomic_write(directory / 'manifest.json', json.dumps(manifest).encode())
            raise ValueError('Layout review failed; destination preserved')
        atomic_write(destination, raw)
        return 'published'
    finally:
        os.close(fd)
        lock.unlink()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workspace', type=Path, default=Path(__file__).resolve().parents[1] / 'workspace')
    sub = parser.add_subparsers(dest='command', required=True)
    check = sub.add_parser('check')
    check.add_argument('targets', nargs='*')
    draft = sub.add_parser('prepare')
    draft.add_argument('replacements', type=Path)
    draft.add_argument('targets', nargs='+')
    draft.add_argument('--session', type=Path)
    commit = sub.add_parser('publish')
    commit.add_argument('session', type=Path)
    commit.add_argument('review', type=Path)
    args = parser.parse_args()
    try:
        if args.command == 'check':
            plan = preflight(args.workspace, args.targets)
            print(json.dumps({'reset': plan['reset'], 'selected': [e for _, e in plan['selected']]}, ensure_ascii=False, indent=2))
        elif args.command == 'prepare':
            print(prepare(args.workspace, args.targets, json.loads(args.replacements.read_text()), args.session))
        else:
            print(publish(args.session, json.loads(args.review.read_text())))
    except (OSError, ValueError, KeyError, TypeError) as error:
        print(str(error), file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
