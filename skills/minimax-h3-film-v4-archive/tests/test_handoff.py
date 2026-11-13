import copy,hashlib,importlib.util,json,pathlib,tempfile,unittest
ROOT=pathlib.Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('handoff',ROOT/'scripts/compile_handoff.py');helper=importlib.util.module_from_spec(spec);spec.loader.exec_module(helper)
class HandoffTests(unittest.TestCase):
 def setUp(self):
  self.workflow=json.loads((ROOT/'references/original-workflow.json').read_text());self.plan=json.loads((ROOT/'examples/lan-15s.plan.json').read_text())
  self.plan['storyboard_review']={'status':'approved','approved_by':'user','approved_revision':self.plan['storyboard_revision'],'evidence':'SYNTHETIC TEST FIXTURE — not a real user approval.'}
 def test_uploaded_workflow_is_exact_original(self):
  self.assertEqual(hashlib.sha256((ROOT/'references/original-workflow.json').read_bytes()).hexdigest(),'983157859d1a043eb7800f0177e6a05234be36a155323a6e3f791c1e1ec6a2ef')
 def test_extracts_wires_in_socket_order(self):
  self.workflow['nodes'].reverse()
  self.assertEqual([s['node_id'] for s in helper.reference_slots(self.workflow)],[27,28,93,104,122,135])
 def test_two_images_and_old_extra_node_explicitly_bypassed(self):
  r=helper.compile_plan(self.plan,self.workflow)
  self.assertEqual([(x['node_id'],x['picture']) for x in r['mapping'] if x['enabled']],[(27,1),(28,2)])
  row=next(x for x in r['mapping'] if x['node_id']==93);self.assertEqual(row['snapshot_mode'],0);self.assertFalse(row['enabled'])
  self.assertEqual(next(x for x in r['node_actions'] if x['node_id']==93)['action'],'Bypass (Ctrl+B)')
 def test_storyboard_only_has_no_dangling_picture_2(self):
  a=self.plan['assets'][1];a['enabled']=False;a['fallback_from_storyboard']=True
  r=helper.compile_plan(self.plan,self.workflow);self.assertNotIn('<Picture 2>',r['prompt']);self.assertEqual(sum(x['enabled'] for x in r['mapping']),1)
 def test_bypass_middle_renumbers_later_asset_once(self):
  self.plan['assets'][1]['enabled']=False;self.plan['assets'][1]['fallback_from_storyboard']=True
  self.plan['assets'][2]['enabled']=True
  self.plan['assets'].append({'id':'PROP_01','role':'prop','node_id':104,'enabled':True,'description_en':'A small wooden sword','file_label':'sword.png'})
  self.plan['video_prompt_template']+='\nWooden sword from {{ref:PROP_01}}.'
  r=helper.compile_plan(self.plan,self.workflow)
  self.assertIn('PROP_01 — A small wooden sword',r['prompt']);self.assertIn('Wooden sword from <Picture 3>',r['prompt'])
  self.assertEqual([(x['asset_id'],x['picture']) for x in r['mapping'] if x['enabled']],[('STORYBOARD',1),('ENV_01',2),('PROP_01',3)])
 def test_missing_asset_is_not_silently_remapped(self):
  self.plan['video_prompt_template']+=' {{ref:CHAR_99}}'
  with self.assertRaisesRegex(ValueError,'chưa khai báo'):helper.compile_plan(self.plan,self.workflow)
 def test_bypass_needs_explicit_storyboard_fallback(self):
  self.plan['assets'][1]['enabled']=False
  with self.assertRaisesRegex(ValueError,'chưa cho phép'):helper.compile_plan(self.plan,self.workflow)
 def test_no_sheet_cannot_disable_storyboard(self):
  self.plan['assets'][0]['enabled']=False
  with self.assertRaisesRegex(ValueError,'STORYBOARD'):helper.compile_plan(self.plan,self.workflow)
 def test_duplicate_asset_or_loader_rejected(self):
  self.plan['assets'].append(copy.deepcopy(self.plan['assets'][1]))
  with self.assertRaises(ValueError):helper.compile_plan(self.plan,self.workflow)
 def test_helper_does_not_add_unwired_images(self):
  self.plan['assets'][1]['node_id']=21
  with self.assertRaisesRegex(ValueError,'không nằm trên dây'):helper.compile_plan(self.plan,self.workflow)
 def test_timestamps_generated_from_single_shot_timeline(self):
  r=helper.compile_plan(self.plan,self.workflow);self.assertIn('[SHOT 2] At 00:04.000',r['prompt']);self.assertIn('[SHOT 3] At 00:07.000',r['prompt']);self.assertIn('[SHOT 4] At 00:12.000',r['prompt'])
  self.assertNotIn('{{',r['prompt']);self.assertNotIn('<Asset:',r['prompt']);self.assertEqual(r['frames'],362)
 def test_shot_total_must_match(self):
  self.plan['shots'][0]['seconds']=1
  with self.assertRaisesRegex(ValueError,'Tổng giây'):helper.compile_plan(self.plan,self.workflow)
 def test_duplicate_grid_position_rejected(self):
  self.plan['shots'][1]['column']=1
  with self.assertRaises(ValueError):helper.compile_plan(self.plan,self.workflow)
 def test_empty_grid_cells_must_be_declared(self):
  self.plan['grid']=[2,3]
  with self.assertRaisesRegex(ValueError,'EMPTY'):helper.compile_plan(self.plan,self.workflow)
  self.plan['empty_cells']=[[1,3],[2,3]];helper.compile_plan(self.plan,self.workflow)
 def test_thirty_seconds_is_not_assumed_gpu_profile(self):
  self.plan['seconds']=30
  with self.assertRaisesRegex(ValueError,'profile'):helper.compile_plan(self.plan,self.workflow)
 def test_invalid_seconds(self):
  for value in [True,float('nan'),float('inf'),0,31]:
   with self.assertRaises(ValueError):helper.frames_for_seconds(value)
 def test_realism_trigger_rejected_for_3d(self):
  self.plan['video_prompt_template']='r34l1sm\n'+self.plan['video_prompt_template']
  with self.assertRaisesRegex(ValueError,'Realism'):helper.compile_plan(self.plan,self.workflow)
 def test_changed_prompt_wiring_needs_readback(self):
  link=next(l for l in self.workflow['links'] if l[0]==7);link[1]=23
  with self.assertRaisesRegex(ValueError,'Prompt'):helper.compile_plan(self.plan,self.workflow)
 def test_write_outputs_does_not_change_original(self):
  p=ROOT/'references/original-workflow.json';before=p.read_bytes();r=helper.compile_plan(self.plan,self.workflow)
  with tempfile.TemporaryDirectory() as d:
   helper.write_handoff(r,d);self.assertTrue((pathlib.Path(d)/'video_prompt.txt').is_file());self.assertTrue((pathlib.Path(d)/'mapping.csv').is_file())
  self.assertEqual(p.read_bytes(),before);self.assertEqual(r['status'],'configuration_to_apply_not_live_runtime_verified')
if __name__=='__main__':unittest.main()
