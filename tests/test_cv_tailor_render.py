import importlib.util
import json
from pathlib import Path
import shutil
import tempfile
import unittest

from scripts import cv_tailor as t
from scripts.cv_tailor_render import render


@unittest.skipUnless(shutil.which('pdflatex') and shutil.which('pdftoppm') and
                     importlib.util.find_spec('pdfplumber'), 'requires LaTeX, Poppler, pdfplumber')
class RenderTests(unittest.TestCase):
    def test_complete_document_geometry_and_failed_compile(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            session = root / 'session'
            session.mkdir()
            raw = br'''\documentclass{article}
\begin{document}
\begin{itemize}
\item ONE alpha \textbf{bold} omega.
\item TWO first line\\SECOND second line.
\item THREE first line\\MIDDLE second line\\LAST third line.
\end{itemize}
\end{document}
'''
            (session / 'candidate.tex').write_bytes(raw)
            manifest = {'workspace': str(root), 'candidate_sha256': t.digest(raw), 'failed_rounds': 0}
            (session / 'manifest.json').write_text(json.dumps(manifest))
            result = render(session)
            words = json.loads((session / 'coordinates.json').read_text())[0]['words']
            positions = {w['text']: w['top'] for w in words}
            self.assertAlmostEqual(positions['ONE'], positions['bold'], delta=2)
            self.assertGreater(positions['SECOND'], positions['TWO'])
            self.assertGreater(positions['MIDDLE'], positions['THREE'])
            self.assertGreater(positions['LAST'], positions['MIDDLE'])
            self.assertTrue(list(session.glob('page-*.png')))
            self.assertEqual(result['pdf_sha256'], t.digest((session / 'candidate.pdf').read_bytes()))
            raw = raw.replace(br'\begin{document}', br'\begin{document}\undefinedcommand')
            (session / 'candidate.tex').write_bytes(raw)
            manifest['candidate_sha256'] = t.digest(raw)
            (session / 'manifest.json').write_text(json.dumps(manifest))
            with self.assertRaisesRegex(ValueError, 'Compilation failed'):
                render(session)
            self.assertFalse((session / 'compilation.json').exists())

    def test_prepare_render_publish_preserves_main(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            raw = (Path(__file__).parent / 'fixtures/parser/synthetic.tex').read_bytes().replace(
                b'\\resumeItem{}', b'\\resumeItem{Built retry controls.}')
            (root / 'main.tex').write_bytes(raw)
            (root / 'job-description.txt').write_text('Software engineer building reliable retry systems')
            plan = t.preflight(root, ['Example Labs'])
            replacements = {b['id']: b['body_latex'] for _, e in plan['selected'] for b in t.bullets(e)}
            session = t.prepare(root, ['Example Labs'], replacements)
            self.addCleanup(lambda: shutil.rmtree(session))
            compilation = render(session)
            pages = json.loads((session / 'coordinates.json').read_text())
            # These short fixture bullets each render on one line. Actual skill review also inspects images.
            self.assertEqual(compilation['pages'], 1)
            words = pages[0]['words']
            start = next(i for i, w in enumerate(words) if w['text'] == 'Reduced')
            end = next(i for i, w in enumerate(words) if w['text'] == 'Projects')
            selected = [w for w in words[start:end] if w['text'] in {'Reduced', 'retries.', 'Built', 'controls.'}]
            self.assertEqual(len(selected), 4)
            self.assertAlmostEqual(selected[0]['top'], selected[1]['top'], delta=2)
            self.assertAlmostEqual(selected[2]['top'], selected[3]['top'], delta=2)
            review = {**compilation, 'images_inspected': True, 'balanced': True,
                      'bullets': {key: {'lines': 1, 'final_line_fill': .7, 'mapping_confident': True}
                                  for key in replacements}}
            self.assertEqual(t.publish(session, review), 'published')
            self.assertEqual((root / 'main.tex').read_bytes(), raw)
            body, state = t.unpack((root / 'tailored.tex').read_bytes())
            self.assertEqual(body, raw)
            self.assertEqual(state['jd_sha256'], plan['jd_sha256'])


if __name__ == '__main__':
    unittest.main()
