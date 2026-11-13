import unittest,json,pathlib,sys,copy
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from audit_workflow import analyze,frames_for_seconds
from synthetic_workflow import synthetic_workflow

class WorkflowAuditTests(unittest.TestCase):
 def setUp(self):self.w=synthetic_workflow()
 def group(self):return next(n for n in self.w['nodes'] if n['id']==105)
 def codes(self,r):return {x['code'] for x in r['findings']}
 def test_reads_exposed_prompt_and_duration_not_internal_demo(self):
  r=analyze(self.w,image_role='storyboard_grid')
  self.assertEqual(r['requested_seconds'],5);self.assertEqual(r['expected_frames'],124)
  self.assertEqual(r['prompt_last_timestamp_seconds'],15)
  self.assertEqual(r['task_node'],'105:104')
 def test_blocks_grid_missing_reference_and_short_duration(self):
  r=analyze(self.w,image_role='storyboard_grid');c=self.codes(r)
  self.assertTrue({'LAYOUT_AS_FIRST_FRAME','MISSING_PICTURE_INPUT','PROMPT_EXCEEDS_DURATION','CHECKPOINT_TASK_NOT_DISTILLED'}<=c)
  self.assertFalse(r['ready'])
 def test_clean_image_and_short_prompt_do_not_certify_fasth3_i2v(self):
  self.group()['widgets_values'][0]='The man in the supplied opening frame looks down at his phone for five seconds.'
  self.group()['widgets_values_named']['prompt']=self.group()['widgets_values'][0]
  r=analyze(self.w,image_role='clean_shot_frame');c=self.codes(r)
  self.assertNotIn('LAYOUT_AS_FIRST_FRAME',c);self.assertNotIn('MISSING_PICTURE_INPUT',c)
  self.assertIn('CHECKPOINT_TASK_NOT_DISTILLED',c);self.assertFalse(r['ready'])
 def test_prompt_duration_changes_do_not_mutate_workflow(self):
  before=copy.deepcopy(self.w);analyze(self.w,image_role='storyboard_grid');self.assertEqual(before,self.w)
 def test_duration_fix_only_removes_duration_failure(self):
  self.group()['widgets_values'][3]=15;self.group()['widgets_values_named']['value_1']=15
  r=analyze(self.w,image_role='storyboard_grid')
  self.assertEqual(r['expected_frames'],362);self.assertNotIn('PROMPT_EXCEEDS_DURATION',self.codes(r))
  self.assertFalse(r['ready'])
 def test_video_metadata_has_priority_over_current_widget(self):
  self.group()['widgets_values'][3]=15;self.group()['widgets_values_named']['value_1']=15
  ex={'a':{'class_type':'MiniMaxH3ImageToVideo','inputs':{'prompt':'00:00–00:15 action','first_frame':['image',0],'length':['math',1]}},'model':{'class_type':'UNETLoader','inputs':{'unet_name':'fastvideo_fasth3_8step_v2_pruned_int8_convrot.safetensors'}},'math':{'class_type':'ComfyMathExpression','inputs':{'values.a':['duration',0]}},'duration':{'class_type':'PrimitiveFloat','inputs':{'value':5}},'image':{'class_type':'LoadImage','inputs':{'image':'board.png'}}}
  r=analyze(self.w,executed=ex,image_role='storyboard_grid')
  self.assertEqual(r['requested_seconds'],5);self.assertEqual(r['settings_source'],'video_prompt_metadata')
  self.assertIn('PROMPT_EXCEEDS_DURATION',self.codes(r))
 def test_real_first_last_inputs_do_not_become_identity_sheet_slots(self):
  self.group()['inputs'][1]['link']=999
  self.w['links'].append([999,136,0,105,1,'IMAGE'])
  r=analyze(self.w,image_role='clean_shot_frame')
  self.assertTrue(r['last_frame_connected']);self.assertNotIn('MISSING_PICTURE_INPUT',self.codes(r))
  self.assertIn('REF2V_PROMPT_IN_I2V',self.codes(r));self.assertFalse(r['ready'])
 def test_missing_group_widget_schema_fails_explicitly(self):
  self.group().pop('widgets_values_named');self.group()['widgets_values'].pop()
  with self.assertRaisesRegex(ValueError,'Cannot safely map'):analyze(self.w)
 def test_original_profile_remains_distinct(self):
  old=json.loads((ROOT/'references/original-workflow.json').read_text());r=analyze(old)
  self.assertEqual(r['task_type'],'MiniMaxH3ReferenceToVideo')
  self.assertEqual(r['profile'],'singularity_original_ref2v')
  self.assertEqual(r['reference_image_count'],3)
 def test_frame_grid(self):
  for sec,frames in [(5,124),(15,362),(0.9,22),(5.8,141),(6.3,158)]:self.assertEqual(frames_for_seconds(sec),frames)
if __name__=='__main__':unittest.main()
