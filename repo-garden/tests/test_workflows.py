import pathlib
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from analyze_forks import classify_fork_evidence
from execute_approved_deletions import deletion_eligibility_errors
from execute_approved_stars import star_eligibility_errors
from inventory_repos import merge_inventory
from reconcile_star_garden import reconcile_record


class WorkflowTests(unittest.TestCase):
    def test_inventory_merge_preserves_analysis_fields(self):
        existing=[{'repo_id':1,'full_name':'granolacowboy/x','safety_status':'PASS_LEVEL1','recommended_disposition':'DEFER'}]
        live=[{'id':1,'full_name':'granolacowboy/x','fork':True,'private':False,'default_branch':'main','updated_at':'2026-01-01T00:00:00Z'}]
        merged=merge_inventory(existing,live)
        self.assertEqual('PASS_LEVEL1',merged[0]['safety_status'])
        self.assertTrue(merged[0]['fork'])

    def test_star_reconciliation_prefers_stable_repo_id(self):
        row={'repo_id':100,'canonical_repo_id':55,'canonical_full_name':'old/name'}
        out=reconcile_record(row,{55:{'id':55,'full_name':'new/name'}},{55:{'repo_id':55,'recommendation':'KEEP_REFERENCE'}})
        self.assertTrue(out['canonical_starred'])
        self.assertEqual('new/name',out['canonical_full_name'])
        self.assertEqual('KEEP_REFERENCE',out['star_garden_recommendation'])

    def test_zero_ahead_single_default_ref_is_safety_pass(self):
        e=classify_fork_evidence(compare={'ahead_by':0,'behind_by':10,'status':'behind'},refs=['refs/heads/main'],default_branch='main',source_accessible=True)
        self.assertEqual('PASS_LEVEL1',e['safety_status'])
        self.assertFalse(e['unique_state'])

    def test_extra_branch_defers_even_with_zero_default_ahead(self):
        e=classify_fork_evidence(compare={'ahead_by':0,'behind_by':10,'status':'behind'},refs=['refs/heads/main','refs/heads/work'],default_branch='main',source_accessible=True)
        self.assertEqual('DEFER',e['safety_status'])
        self.assertTrue(e['unique_state'])

    def test_delete_requires_safety_and_dependencies(self):
        approval={'repo_id':1,'full_name':'granolacowboy/x','approved_at':'x','approved_by':'Roo'}
        record={'repo_id':1,'full_name':'granolacowboy/x','safety_status':'PASS_LEVEL1','recommended_disposition':'DELETE_REDUNDANT_FORK','preservation_complete':True,'star_dependency_complete':True}
        self.assertEqual([],deletion_eligibility_errors(approval,record))
        record['star_dependency_complete']=False
        self.assertTrue(deletion_eligibility_errors(approval,record))

    def test_star_executor_requires_canonical_target_and_approval(self):
        row={'repo_id':55,'full_name':'owner/repo','approved_at':'x','approved_by':'Roo'}
        self.assertEqual([],star_eligibility_errors(row))
        del row['approved_at']
        self.assertTrue(star_eligibility_errors(row))


if __name__ == '__main__': unittest.main()
