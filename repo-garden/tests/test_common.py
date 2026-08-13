import hashlib
import pathlib
import sys
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from _common import atomic_write_jsonl, batch_digest, is_not_found_error, load_jsonl


class CommonTests(unittest.TestCase):
    def test_batch_digest_is_order_independent_and_identity_bound(self):
        rows_a = [{'repo_id':2,'full_name':'granolacowboy/b'},{'repo_id':1,'full_name':'granolacowboy/a'}]
        rows_b = list(reversed(rows_a))
        self.assertEqual(batch_digest(rows_a), batch_digest(rows_b))
        expected = hashlib.sha256(b'1:granolacowboy/a\n2:granolacowboy/b\n').hexdigest()[:16]
        self.assertEqual(expected, batch_digest(rows_a))

    def test_atomic_jsonl_round_trip(self):
        with tempfile.TemporaryDirectory() as td:
            path = pathlib.Path(td) / 'rows.jsonl'
            rows = [{'repo_id':1},{'repo_id':2}]
            atomic_write_jsonl(path, rows)
            self.assertEqual(rows, load_jsonl(path))

    def test_not_found_parser_accepts_github_404(self):
        self.assertTrue(is_not_found_error('HTTP 404: Not Found'))
        self.assertFalse(is_not_found_error('HTTP 403: Forbidden'))


if __name__ == '__main__': unittest.main()
