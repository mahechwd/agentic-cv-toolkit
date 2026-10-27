"""Render a private complete CV candidate for agent-reviewed layout verification."""
import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time

if __package__ in {None, ''}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts.cv_tailor import atomic_write, digest


def render(session, engine='pdflatex'):
    if engine not in {'pdflatex', 'xelatex', 'lualatex'}:
        raise ValueError('Unsupported compiler')
    compiler, rasterizer = shutil.which(engine), shutil.which('pdftoppm')
    if not compiler or not rasterizer:
        raise ValueError('Local LaTeX compiler and pdftoppm required; destination preserved')
    import pdfplumber
    directory = Path(session).resolve()
    manifest = json.loads((directory / 'manifest.json').read_text())
    if manifest['failed_rounds'] >= 3:
        raise ValueError('Three failed layout rounds reached')
    candidate = directory / 'candidate.tex'
    candidate_hash = digest(candidate.read_bytes())
    if candidate_hash != manifest['candidate_sha256']:
        raise ValueError('Candidate changed after preparation')
    (directory / 'compilation.json').unlink(missing_ok=True)
    (directory / 'candidate.pdf').unlink(missing_ok=True)
    for image in directory.glob('page-*.png'):
        image.unlink()
    started = time.monotonic()
    env = os.environ.copy()
    workspace = Path(manifest['workspace'])
    env['TEXINPUTS'] = str(workspace) + os.pathsep + env.get('TEXINPUTS', '')
    command = [compiler, '-no-shell-escape', '-halt-on-error', '-interaction=nonstopmode',
               '-recorder', '-output-directory=' + str(directory), str(candidate)]
    for run in range(2):
        result = subprocess.run(command, cwd=workspace, env=env, capture_output=True, timeout=120)
        (directory / f'compiler-{run + 1}.log').write_bytes(result.stdout + result.stderr)
        if result.returncode:
            raise ValueError(f'Compilation failed; inspect compiler-{run + 1}.log in session')
    pdf = directory / 'candidate.pdf'
    if not pdf.exists() or digest(candidate.read_bytes()) != candidate_hash:
        raise ValueError('Missing PDF or candidate changed during compilation')
    with pdfplumber.open(pdf) as document:
        pages = [{'page': p.page_number, 'width': p.width, 'height': p.height,
                  'words': p.extract_words(x_tolerance=2, y_tolerance=2)} for p in document.pages]
    atomic_write(directory / 'coordinates.json', json.dumps(pages, indent=2).encode())
    subprocess.run([rasterizer, '-r', '120', '-png', str(pdf), str(directory / 'page')],
                   check=True, capture_output=True, timeout=120)
    if not list(directory.glob('page-*.png')):
        raise ValueError('No rendered page images')
    dependencies = {}
    for line in (directory / 'candidate.fls').read_text().splitlines():
        if line.startswith('INPUT '):
            path = Path(line[6:])
            path = (workspace / path).resolve() if not path.is_absolute() else path.resolve()
            if path.is_file() and not path.is_relative_to(directory):
                dependencies[str(path)] = digest(path.read_bytes())
    result = {'candidate_sha256': candidate_hash, 'pdf_sha256': digest(pdf.read_bytes()),
              'engine': engine, 'compiler_version': subprocess.check_output([compiler, '--version'], text=True).splitlines()[0],
              'elapsed_seconds': round(time.monotonic() - started, 3), 'dependencies': dependencies,
              'pages': len(pages)}
    atomic_write(directory / 'compilation.json', json.dumps(result, indent=2).encode())
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('session', type=Path)
    parser.add_argument('--engine', choices=['pdflatex', 'xelatex', 'lualatex'], default='pdflatex')
    args = parser.parse_args()
    try:
        print(json.dumps(render(args.session, args.engine), indent=2))
    except (OSError, ValueError, ImportError, subprocess.SubprocessError) as error:
        print(str(error), file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
