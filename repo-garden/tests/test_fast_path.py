import pathlib, sys, unittest
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from analyze_forks import metadata_fast_path_eligible

class FastPathTests(unittest.TestCase):
    def test_pre_fork_push_with_accessible_source_is_eligible(self):
        meta={'fork':True,'created_at':'2025-05-24T11:00:00Z','pushed_at':'2025-05-24T10:00:00Z','has_pages':False,'open_issues_count':0,'has_discussions':False,'disabled':False,'parent':{'id':1,'full_name':'owner/repo'},'source':{'id':1,'full_name':'owner/repo'}}
        self.assertTrue(metadata_fast_path_eligible(meta))
    def test_later_push_or_missing_source_is_not_eligible(self):
        meta={'fork':True,'created_at':'2025-05-24T11:00:00Z','pushed_at':'2025-05-25T10:00:00Z','has_pages':False,'open_issues_count':0,'has_discussions':False,'disabled':False,'parent':{'id':1,'full_name':'owner/repo'},'source':{'id':1,'full_name':'owner/repo'}}
        self.assertFalse(metadata_fast_path_eligible(meta))
        meta['pushed_at']='2025-05-24T10:00:00Z'; meta['parent']=None; meta['source']=None
        self.assertFalse(metadata_fast_path_eligible(meta))
if __name__=='__main__': unittest.main()
