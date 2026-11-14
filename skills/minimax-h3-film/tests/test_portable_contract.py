"""Synthetic contracts only: no private storyboard, dialogue, character, or new film example."""
import copy,importlib.util,pathlib,unittest
ROOT=pathlib.Path(__file__).resolve().parents[1]
def load(name):
 s=importlib.util.spec_from_file_location(name,ROOT/'scripts'/(name+'.py'));m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
v=load('validate_handoff');a=load('audit_render_prompt')
def fixture():
 panels=[];shots=[];blocks=[]
 for i in range(1,5):
  panel={'id':i,'row':(i-1)//2+1,'column':(i-1)%2+1,'empty':False,'source_interval':[(i-1)*2.5,i*2.5]};panels.append(panel)
  s={'id':i,'panel_id':i,'start_s':(i-1)*2.5,'end_s':i*2.5,'panel_anchor_en':f'panel fixture {i}','camera_size_en':['extreme close-up','medium close-up','extreme close-up','close-up'][i-1],'camera_angle_en':['side angle','frontal angle','tilted angle','frontal angle'][i-1],'start_state_en':f'state fixture start {i}','action_en':f'action fixture {i}','end_state_en':f'state fixture end {i}','transition_en':'' if i==1 else 'Hard cut'};shots.append(s)
  action={'event_id':f'EVENT_{i}','phase':'complete','occurrences':1,'state_before':{'TEST_OBJECT':{'step':i-1}},'state_after':{'TEST_OBJECT':{'step':i}},'completion_en':f'completion fixture {i}','hold_en':f'hold fixture {i}'};s['actions']=[action]
  blocks.append(f'[Shot {i}] [{s["start_s"]}-{s["end_s"]}s] '+'. '.join(s[k] for k in ['panel_anchor_en','transition_en','camera_size_en','camera_angle_en','start_state_en','action_en','end_state_en'])+'. '+action['completion_en']+'. '+action['hold_en'])
 return {'storyboard_revision':'TEST_REV','storyboard_review':{'status':'approved','approved_by':'user','approved_revision':'TEST_REV','evidence':'Synthetic approval fixture; never a real project approval.'},'seconds':10,'workflow_mode':'ref2v','editing_mode':'cuts','panels':panels,'shots':shots,'assets':[{'picture':1,'role':'storyboard','active':True,'connected':True}],'characters':[],'audio':{'dialogue':[]},'initial_states':{'TEST_OBJECT':{'step':0}},'expected_final_states':{'TEST_OBJECT':{'step':4}},'video_prompt_en':'Picture 1 is the synthetic test storyboard.\n'+'\n'.join(blocks)}
def codes(p):return {x['code'] for x in v.validate(p)['errors']}
def add_voice(p):
 voice={'status':'approved','approval_evidence':'Synthetic user choice.','voice_anchor_en':'Vietnamese voice with warm low pitch and measured pace.','accent':'north','pitch':'low','timbre':'warm','pace':'measured','generation_mode':'native_exploratory','delivery_choice_evidence':'Synthetic acceptance of exploratory audio.','verification':{'status':'untested'},'strict_identity_required':False}
 p['characters']=[{'character_id':'TEST_A','voice':voice}];p['audio']['dialogue']=[{'utterance_id':'LINE_1','character_id':'TEST_A','text':'Câu kiểm thử.','start_s':0,'end_s':1,'timing_check':{'method':'estimate','duration_s':.8,'basis':'Synthetic timing fixture.'}}];p['video_prompt_en']+='\n'+voice['voice_anchor_en']+' Câu kiểm thử.';return voice

class ContractTests(unittest.TestCase):
 def test_four_panels_four_blocks(self):self.assertTrue(v.validate(fixture())['valid'])
 def test_regression_four_panels_collapsed_to_two(self):
  p=fixture();p['shots']=p['shots'][:2];p['video_prompt_en']='Picture 1. [Shot 1] [0-5s] summary. [Shot 2] [5-10s] summary.';self.assertIn('shot_count',codes(p))
 def test_no_shot_blocks_in_continuous_summary(self):
  p=fixture();p['video_prompt_en']='Picture 1. A continuous close-up sequence, static steady close-up throughout.';self.assertTrue({'prompt_shot_coverage','contradictory_one_take'}<=codes(p))
 def test_forbidding_one_take_is_not_a_positive_one_take_request(self):
  p=fixture();p['video_prompt_en']+=' Do not render one continuous shot.';self.assertNotIn('contradictory_one_take',codes(p))
 def test_four_labels_without_distinct_details_fails(self):
  p=fixture();p['video_prompt_en']='Picture 1. '+' '.join(f'[Shot {s["id"]}] [{s["start_s"]}-{s["end_s"]}s] same subject, then smiles.' for s in p['shots']);self.assertIn('shot_detail_omitted',codes(p))
 def test_missing_camera_angle_detected(self):
  p=fixture();p['video_prompt_en']=p['video_prompt_en'].replace('tilted angle','');self.assertIn('shot_detail_omitted',codes(p))
 def test_wrong_shot_size_detected(self):
  p=fixture();p['video_prompt_en']=p['video_prompt_en'].replace('medium close-up','close-up');self.assertIn('shot_detail_omitted',codes(p))
 def test_reordered_panels_fail(self):
  p=fixture();p['shots'][1]['panel_id']=4;p['shots'][3]['panel_id']=2;self.assertIn('panel_order',codes(p))
 def test_caption_duplicate_time_requires_resolution(self):
  p=fixture();p['panels'][1]['source_interval']=[0,2.5];self.assertIn('source_timing_conflict',codes(p))
 def test_source_gap_requires_resolution(self):
  p=fixture();p['panels'][1]['source_interval']=[3,5];self.assertIn('source_timing_conflict',codes(p))
 def test_caption_changed_without_permission_fails(self):
  p=fixture();p['panels'][-1]['source_interval']=[7.5,9];self.assertIn('source_timing_conflict',codes(p))
 def test_timing_approval_can_resolve_conflict(self):
  p=fixture();p['panels'][1]['source_interval']=[0,2.5];p['timing_resolution']={'authority':'explicit_user_approval','evidence':'Synthetic choice of revised test timing.'};self.assertTrue(v.validate(p)['valid'])
 def test_delegated_timing_record_accepted(self):
  p=fixture();p['panels'][1]['source_interval']=[0,2.5];p['timing_resolution']={'authority':'user_delegated_timing','evidence':'Synthetic permission to choose test timing.'};self.assertTrue(v.validate(p)['valid'])
 def test_final_timeline_overlap_fails(self):
  p=fixture();p['shots'][2]['start_s']=4;self.assertIn('timeline_overlap_or_gap',codes(p))
 def test_final_duration_wrong_fails(self):
  p=fixture();p['seconds']=11;self.assertIn('timeline_total',codes(p))
 def test_prompt_timestamp_not_table_fails(self):
  p=fixture();p['video_prompt_en']=p['video_prompt_en'].replace('[0.0-2.5s]','[0-3s]');self.assertIn('prompt_time_mismatch',codes(p))
 def test_empty_panel_not_a_shot(self):
  p=fixture();p['panels'].append({'id':5,'row':3,'column':1,'empty':True});self.assertTrue(v.validate(p)['valid'])
 def test_approval_missing_fails(self):
  p=fixture();p['storyboard_review']['status']='pending';self.assertIn('storyboard_not_approved',codes(p))
 def test_revision_changed_requires_review(self):
  p=fixture();p['storyboard_revision']='CHANGED';self.assertIn('revision_mismatch',codes(p))
 def test_phantom_reference_fails(self):
  p=fixture();p['video_prompt_en']+=' Picture 2';self.assertIn('phantom_picture',codes(p))
 def test_sheet_as_i2v_first_frame_fails(self):
  p=fixture();p['workflow_mode']='i2v';p['assets']=[{'picture':1,'role':'character_sheet','active':True,'connected':True,'socket':'first_frame'}];self.assertIn('grid_to_frame',codes(p))
 def test_silent_clip_pending_voice_allowed(self):
  p=fixture();p['characters']=[{'character_id':'TEST_A','voice':{'status':'pending'}}];self.assertTrue(v.validate(p)['valid'])
 def test_spoken_clip_pending_voice_rejected(self):
  p=fixture();add_voice(p)['status']='pending';self.assertIn('voice_not_approved',codes(p))
 def test_confirmed_voice_and_exact_dialogue(self):
  p=fixture();add_voice(p);self.assertTrue(v.validate(p)['valid'])
 def test_voice_anchor_omitted(self):
  p=fixture();voice=add_voice(p);p['video_prompt_en']=p['video_prompt_en'].replace(voice['voice_anchor_en'],'');self.assertIn('voice_anchor_missing',codes(p))
 def test_dialogue_not_paraphrased(self):
  p=fixture();add_voice(p);p['video_prompt_en']=p['video_prompt_en'].replace('Câu kiểm thử.','Other text.');self.assertIn('dialogue_modified',codes(p))
 def test_two_voice_ids_same_anchor_rejected(self):
  p=fixture();voice=add_voice(p);p['characters'].append({'character_id':'TEST_B','voice':copy.deepcopy(voice)});p['audio']['dialogue'].append({'character_id':'TEST_B','text':'Câu kiểm thử.','start_s':2,'end_s':3});self.assertTrue({'identical_character_voices','voices_not_distinct'}<=codes(p))
 def test_two_character_voices_differ_in_two_attributes(self):
  p=fixture();voice=add_voice(p);second=copy.deepcopy(voice);second.update(pitch='high',timbre='bright',voice_anchor_en='Vietnamese voice with bright high pitch and measured pace.');p['characters'].append({'character_id':'TEST_B','voice':second});p['audio']['dialogue'].append({'utterance_id':'LINE_2','character_id':'TEST_B','text':'Câu kiểm thử.','start_s':2,'end_s':3,'timing_check':{'method':'estimate','duration_s':.8,'basis':'Synthetic timing fixture.'}});p['video_prompt_en']+=' '+second['voice_anchor_en'];self.assertTrue(v.validate(p)['valid'])
 def test_unknown_speaker_rejected(self):
  p=fixture();add_voice(p);p['audio']['dialogue'][0]['character_id']='MISSING';self.assertIn('unknown_speaker',codes(p))
 def test_node_prompt_links_resolved_read_only(self):
  api={'136':{'class_type':'MiniMaxH3ReferenceToVideo','inputs':{'prompt':['138',0]}},'138':{'class_type':'PrimitiveStringMultiline','inputs':{'value':'test fixture'}}};self.assertEqual(a.get_prompt(api),('test fixture','138'))
 def test_actual_llm_output_not_inferred_from_its_input(self):
  api={'136':{'class_type':'MiniMaxH3ReferenceToVideo','inputs':{'prompt':['200',0]}},'200':{'class_type':'LLMRewrite','inputs':{'prompt':'not the generated output'}}}
  with self.assertRaises(ValueError):a.get_prompt(api)
 def test_rendered_missing_blocks_does_not_match_expected(self):
  r=a.compare('[Shot 1] [Shot 2] [Shot 3] [Shot 4]','A continuous close-up sequence.');self.assertFalse(r['prompt_matches']);self.assertEqual(r['rendered_shot_labels'],[])
 def test_newline_convention_not_false_difference(self):self.assertTrue(a.compare('test\r\nfixture\n','test\nfixture')['prompt_matches'])

if __name__=='__main__':unittest.main(verbosity=2)
