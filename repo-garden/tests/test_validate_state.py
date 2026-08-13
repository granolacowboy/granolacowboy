import pathlib
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from validate_state import validate_approval_rows


class ValidationTests(unittest.TestCase):
    def test_control_repo_cannot_be_approved_for_deletion(self):
        errors=validate_approval_rows([{'repo_id':1,'full_name':'granolacowboy/github-star-garden','approved_at':'2026-01-01','approved_by':'Roo'}],kind='deletion')
        self.assertTrue(any('control repository' in e for e in errors))

    def test_approval_requires_identity_and_evidence(self):
        self.assertTrue(validate_approval_rows([{'full_name':'granolacowboy/x'}],kind='deletion'))


if __name__ == '__main__': unittest.main()
