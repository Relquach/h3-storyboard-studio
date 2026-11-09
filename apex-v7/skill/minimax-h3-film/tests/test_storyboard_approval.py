import unittest,pathlib,json,sys,copy
ROOT=pathlib.Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from compile_handoff import compile_plan,validate_storyboard_approval
class StoryboardApprovalTests(unittest.TestCase):
 def setUp(self):
  self.plan=json.loads((ROOT/'examples/lan-15s.plan.json').read_text());self.workflow=json.loads((ROOT/'references/original-workflow.json').read_text())
 def test_unapproved_example_cannot_compile_prompt(self):
  with self.assertRaisesRegex(ValueError,'chưa được người dùng duyệt'):compile_plan(self.plan,self.workflow)
 def test_missing_approval_is_not_initial_request_approval(self):
  self.plan.pop('storyboard_review')
  with self.assertRaises(ValueError):validate_storyboard_approval(self.plan)
 def test_synthetic_approval_for_current_revision_allows_compile(self):
  self.plan['storyboard_review']={'status':'approved','approved_by':'user','approved_revision':self.plan['storyboard_revision'],'evidence':'SYNTHETIC TEST ONLY: dùng bản này'}
  self.assertIn('<Picture 2>',compile_plan(self.plan,self.workflow)['prompt'])
 def test_new_image_revision_invalidates_old_approval(self):
  self.plan['storyboard_review']={'status':'approved','approved_by':'user','approved_revision':'old-revision','evidence':'SYNTHETIC TEST ONLY'}
  with self.assertRaisesRegex(ValueError,'Revision'):validate_storyboard_approval(self.plan)
 def test_self_approval_and_empty_evidence_are_rejected(self):
  self.plan['storyboard_review']={'status':'approved','approved_by':'assistant','approved_revision':self.plan['storyboard_revision'],'evidence':'looks good'}
  with self.assertRaises(ValueError):validate_storyboard_approval(self.plan)
  self.plan['storyboard_review']['approved_by']='user';self.plan['storyboard_review']['evidence']=''
  with self.assertRaisesRegex(ValueError,'Thiếu lời'):validate_storyboard_approval(self.plan)
if __name__=='__main__':unittest.main()
