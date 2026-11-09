import copy,importlib.util,json,pathlib,unittest
ROOT=pathlib.Path(__file__).resolve().parents[1];spec=importlib.util.spec_from_file_location('apex_handoff',ROOT/'scripts/apex_handoff.py');h=importlib.util.module_from_spec(spec);spec.loader.exec_module(h)
class ApexTests(unittest.TestCase):
 def setUp(self):
  self.w=json.loads((ROOT/'references/apex-v7-studio-h3.json').read_text());self.p=json.loads((ROOT/'examples/apex-pending.plan.json').read_text())
 def approved(self):
  self.p['storyboard_revision']='TEST';self.p['storyboard_review']={'status':'approved','approved_by':'user','approved_revision':'TEST','evidence':'SYNTHETIC TEST ONLY'};self.p['video_prompt_template']='[SHOT 1] {{start:SHOT 1}}–{{end:SHOT 1}} {{ref:STORYBOARD}}';return self.p
 def test_approval_gate(self):
  with self.assertRaises(ValueError):h.compile_plan(self.p,self.w)
 def test_changed_revision_gate(self):
  p=self.approved();p['storyboard_revision']='NEW'
  with self.assertRaises(ValueError):h.compile_plan(p,self.w)
 def test_false_user_claim_rejected(self):
  p=self.approved();p['storyboard_review']['approved_by']='assistant'
  with self.assertRaises(ValueError):h.compile_plan(p,self.w)
 def test_compact_picture_numbers(self):
  p=self.approved();p['assets'].append({'id':'ENV','loader':9409,'file':'TEST.png','description_en':'test environment'});p['video_prompt_template']+=' {{ref:ENV}}';r=h.compile_plan(p,self.w);self.assertIn('<Picture 2>',r['prompt']);self.assertNotIn('<Picture 3>',r['prompt'])
 def test_default_does_not_claim_sheet(self):
  r=h.compile_plan(self.approved(),self.w);self.assertNotIn('<Picture 2>',r['prompt'])
 def test_unprovided_sheet_rejected(self):
  p=self.approved();p['video_prompt_template']+=' {{ref:CHAR}}'
  with self.assertRaises(ValueError):h.compile_plan(p,self.w)
 def test_unwired_asset_rejected(self):
  p=self.approved();p['assets'][0]['loader']=999
  with self.assertRaises(ValueError):h.compile_plan(p,self.w)
 def test_read_only(self):
  before=copy.deepcopy(self.w);h.compile_plan(self.approved(),self.w);self.assertEqual(before,self.w)
 def test_grid_mismatch(self):
  p=self.approved();p['grid']=[2,2]
  with self.assertRaises(ValueError):h.compile_plan(p,self.w)
 def test_no_phantom_hardcoded_picture(self):
  p=self.approved();p['video_prompt_template']+=' <Picture 9>'
  with self.assertRaises(ValueError):h.compile_plan(p,self.w)
 def test_timing_and_audit(self):
  self.assertEqual([h.frames(t) for t in [5,10,15]],[124,243,362]);r=h.audit(self.w);self.assertEqual(r['stages'],2);self.assertFalse(r['llm_present']);self.assertEqual(len(r['references']),4)
if __name__=='__main__':unittest.main()
