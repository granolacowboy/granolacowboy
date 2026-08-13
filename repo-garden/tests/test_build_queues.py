import pathlib
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from build_queues import derive_queue


class QueueTests(unittest.TestCase):
    def test_starred_safe_redundant_fork_is_delete(self):
        row={'full_name':'granolacowboy/x','fork':True,'safety_status':'PASS_LEVEL1','canonical_starred':True,'unique_state':False}
        self.assertEqual('DELETE_REDUNDANT_FORK',derive_queue(row))

    def test_unstarred_worthwhile_safe_fork_is_star_then_delete(self):
        row={'full_name':'granolacowboy/x','fork':True,'safety_status':'PASS_LEVEL1','canonical_starred':False,'star_garden_recommendation':'KEEP_REFERENCE','unique_state':False}
        self.assertEqual('STAR_UPSTREAM_THEN_DELETE',derive_queue(row))

    def test_unknown_star_status_defers(self):
        row={'full_name':'granolacowboy/x','fork':True,'safety_status':'PASS_LEVEL1','canonical_starred':None,'unique_state':False}
        self.assertEqual('DEFER',derive_queue(row))

    def test_unique_fork_never_routes_to_delete(self):
        row={'full_name':'granolacowboy/x','fork':True,'safety_status':'PASS_LEVEL1','canonical_starred':True,'unique_state':True}
        self.assertEqual('KEEP_CUSTOM_FORK',derive_queue(row))


if __name__ == '__main__': unittest.main()
