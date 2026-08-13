import pathlib, sys, unittest
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from seed_structural_cohorts import cohort_query

class SeedTests(unittest.TestCase):
    def test_level0_query_bounds_push_before_next_day(self):
        self.assertEqual('user:granolacowboy fork:only created:2025-05-24 pushed:<2025-05-25',cohort_query('2025-05-24','level0'))
    def test_level1_query_bounds_later_push(self):
        self.assertEqual('user:granolacowboy fork:only created:2025-05-24 pushed:>2025-05-24',cohort_query('2025-05-24','level1'))
if __name__=='__main__': unittest.main()
