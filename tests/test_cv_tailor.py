import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from scripts import cv_tailor as t


class TailorTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.workspace = Path(self.temp.name)
        self.raw = (Path(__file__).parent / 'fixtures/parser/synthetic.tex').read_bytes().replace(
            b'\\resumeItem{}', b'\\resumeItem{Built retry controls.}')
        (self.workspace / 'main.tex').write_bytes(self.raw)
        (self.workspace / 'job-description.txt').write_text('Software engineer\n Python')

    def plan(self, targets=None):
        return t.preflight(self.workspace, targets or ['section:Experience'])

    def bodies(self, plan):
        return {b['id']: b['body_latex'] for _, e in plan['selected'] for b in t.bullets(e)}

    def store(self, raw=None):
        (self.workspace / 'tailored.tex').write_bytes(t.pack(raw or self.raw, self.plan()['jd_sha256']))

    def test_jd_checked_before_invalid_main_and_targets(self):
        (self.workspace / 'job-description.txt').write_text(' ')
        (self.workspace / 'main.tex').write_text('invalid')
        with self.assertRaisesRegex(ValueError, 'job-description'):
            self.plan(['unknown'])

    def test_missing_corrupt_and_manually_edited_state(self):
        path = self.workspace / 'tailored.tex'
        for raw in (self.raw, t.PREFIX + b'{}\n' + self.raw,
                    t.pack(self.raw, self.plan()['jd_sha256']) + b'changed'):
            path.write_bytes(raw)
            with self.assertRaisesRegex(ValueError, 'state'):
                self.plan()

    def test_whitespace_only_jd_and_changed_jd(self):
        self.store()
        (self.workspace / 'job-description.txt').write_text(' Software   engineer Python\n')
        self.assertFalse(self.plan()['reset'])
        (self.workspace / 'job-description.txt').write_text('Different role')
        self.assertTrue(self.plan()['reset'])

    def test_overlap_deduplicated_and_empty_slot_stops_everything(self):
        plan = self.plan(['section:Experience', 'Example Labs'])
        self.assertEqual(len(plan['selected']), 1)
        (self.workspace / 'main.tex').write_bytes(self.raw.replace(b'Built retry controls.', b''))
        with self.assertRaisesRegex(ValueError, 'cv-build'):
            self.plan(['section:Experience', 'section:Projects'])
        self.assertFalse((self.workspace / 'tailored.tex').exists())

    def test_repeat_uses_canonical_and_preserves_unselected_bytes(self):
        old = self.raw.replace(b'Built retry controls.', b'Old tailored sentence.').replace(
            b'Built a queue simulator', b'Created a queue simulator')
        self.store(old)
        plan = self.plan()
        body, _ = t.unpack(t.candidate(plan, self.bodies(plan)))
        self.assertEqual(body, old.replace(b'Old tailored sentence.', b'Built retry controls.'))

    def test_bullet_count_sync_both_directions(self):
        for old, main in ((self.raw, self.raw.replace(b'\\resumeItem{Built retry controls.}',
                                b'\\resumeItem{Built retry controls.}\n\\resumeItem{Added tests.}')),
                          (self.raw.replace(b'\\resumeItem{Built retry controls.}',
                                b'\\resumeItem{Built retry controls.}\n\\resumeItem{Added tests.}'), self.raw)):
            (self.workspace / 'main.tex').write_bytes(main)
            # Reset the destination directly, with valid metadata.
            (self.workspace / 'tailored.tex').write_bytes(t.pack(old, t.jd_hash((self.workspace / 'job-description.txt').read_bytes())))
            plan = self.plan()
            body, _ = t.unpack(t.candidate(plan, self.bodies(plan)))
            self.assertEqual(body, main)

    def test_generated_syntax_and_unselected_ids_rejected(self):
        for body in ('Bad % value', r'\input{secret}', r'\resumeItem{extra}', 'Bad }', r'\small text'):
            with self.assertRaises(ValueError):
                t.validate_body(body)
        t.validate_body(r'Improved \textbf{25\%} of retries \& escaped values.')
        plan = self.plan()
        with self.assertRaises(ValueError):
            t.candidate(plan, {})

    def make_session(self):
        plan = self.plan()
        session = t.prepare(self.workspace, plan['targets'], self.bodies(plan))
        self.addCleanup(lambda: __import__('shutil').rmtree(session))
        return session

    def fake_review(self, session):
        # Unit tests isolate publication; real renderer tests cover actual PDFs.
        manifest = json.loads((session / 'manifest.json').read_text())
        (session / 'candidate.pdf').write_bytes(b'synthetic stand-in')
        compilation = {'candidate_sha256': manifest['candidate_sha256'],
                       'pdf_sha256': t.digest(b'synthetic stand-in')}
        (session / 'compilation.json').write_text(json.dumps(compilation))
        return {**compilation, 'images_inspected': True, 'balanced': True,
                'bullets': {key: {'lines': 2, 'final_line_fill': .6, 'mapping_confident': True}
                            for key in manifest['replacements']}}

    def test_publish_and_unchanged(self):
        session = self.make_session()
        review = self.fake_review(session)
        self.assertEqual(t.publish(session, review), 'published')
        second = self.make_session()
        self.assertEqual(t.publish(second, {}), 'unchanged')

    def test_failed_reset_preserves_destination_and_stops_after_three(self):
        self.store()
        before = (self.workspace / 'tailored.tex').read_bytes()
        (self.workspace / 'job-description.txt').write_text('New vacancy')
        session = self.make_session()
        review = self.fake_review(session)
        review['balanced'] = False
        for _ in range(3):
            with self.assertRaisesRegex(ValueError, 'Layout review failed'):
                t.publish(session, review)
        review['balanced'] = True
        with self.assertRaisesRegex(ValueError, 'Three failed'):
            t.publish(session, review)
        self.assertEqual((self.workspace / 'tailored.tex').read_bytes(), before)

    def test_stale_input_candidate_review_and_atomic_failure(self):
        session = self.make_session()
        review = self.fake_review(session)
        review['pdf_sha256'] = 'stale'
        with self.assertRaisesRegex(ValueError, 'Review is stale'):
            t.publish(session, review)
        review = self.fake_review(session)
        with patch.object(t.os, 'replace', side_effect=OSError('interrupted')):
            with self.assertRaises(OSError):
                t.publish(session, review)
        self.assertFalse((self.workspace / 'tailored.tex').exists())
        (self.workspace / 'main.tex').write_bytes(self.raw + b'\n')
        with self.assertRaisesRegex(ValueError, 'Inputs changed'):
            t.publish(session, review)
        self.assertFalse((self.workspace / '.cv-tailor.lock').exists())


if __name__ == '__main__':
    unittest.main()
