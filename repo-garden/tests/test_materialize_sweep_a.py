import pathlib,sys,unittest
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from materialize_sweep_a import disposition_for, star_set_complete

class MaterializeTests(unittest.TestCase):
    def test_star_set_complete_requires_expected_count_match(self):
        self.assertTrue(star_set_complete(2664,2664))
        self.assertFalse(star_set_complete(2663,2664))
        self.assertFalse(star_set_complete(2664,None))
    def test_safe_star_overlap_is_delete_redundant(self):
        self.assertEqual('DELETE_REDUNDANT_FORK',disposition_for({'safety_status':'PASS_METADATA_FAST_PATH','canonical_starred':True,'unique_state':False}))
    def test_safe_nonstarred_stays_deferred_for_star_value_review(self):
        self.assertEqual('DEFER',disposition_for({'safety_status':'PASS_LEVEL1','canonical_starred':False,'unique_state':False}))
if __name__=='__main__': unittest.main()
