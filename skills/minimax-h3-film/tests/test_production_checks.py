"""Synthetic regression data only; no user's film, voice, footage or spoken script."""
import copy,unittest
from test_portable_contract import fixture,add_voice,codes,v,a
prod=v.production

class ProductionTests(unittest.TestCase):
 def test_ui_handoff_copied_into_prompt_is_rejected(self):
  p=fixture();p['video_prompt_en']='BẬT loader:[27]\n#62=true; #23=15;\nCHỈ SAO CHÉP NỘI DUNG TRONG KHỐI DƯỚI VÀO#70:\n```text\n'+p['video_prompt_en'];self.assertTrue({'prompt_ui_instructions','prompt_node_assignments','prompt_code_fence'}<=codes(p))
 def test_unrelated_number_in_dialogue_not_node_assignment(self):self.assertEqual(prod.prompt_hygiene('A test number 123, not a UI command.'),[])
 def test_finite_event_cannot_replay_after_completion(self):
  p=fixture();p['shots'][1]['actions'][0]['event_id']='EVENT_1';self.assertIn('completed_event_replayed',codes(p))
 def test_previous_prop_state_cannot_reset(self):
  p=fixture();p['shots'][1]['actions'][0]['state_before']['TEST_OBJECT']['step']=0;self.assertIn('state_reset',codes(p))
 def test_initial_state_required_for_tracked_prop(self):
  p=fixture();p['initial_states']={};self.assertIn('unknown_state_object',codes(p))
 def test_only_saying_once_is_insufficient(self):
  p=fixture();del p['shots'][0]['actions'][0]['state_after'];self.assertIn('missing_action_states',codes(p))
 def test_endpoint_and_hold_need_to_reach_model_text(self):
  p=fixture();p['video_prompt_en']=p['video_prompt_en'].replace('hold fixture 1','');self.assertIn('action_endpoint_omitted',codes(p))
 def test_unknown_next_action_cannot_restart_running_event(self):
  p=fixture();p['shots'][0]['actions'][0]['phase']='start';p['shots'][1]['actions'][0].update(event_id='EVENT_1',phase='start');self.assertIn('action_restarted',codes(p))
 def test_legitimate_event_continues_across_shots_without_replay(self):
  p=fixture();p['shots'][0]['actions'][0]['phase']='start';p['shots'][1]['actions'][0].update(event_id='EVENT_1',phase='continue');p['shots'][2]['actions'][0].update(event_id='EVENT_1',phase='complete');self.assertTrue(v.validate(p)['valid'])
 def test_unfinished_event_needs_explicit_carry(self):
  p=fixture();p['shots'][-1]['actions'][0]['phase']='start';self.assertIn('unfinished_events',codes(p));p['carry_actions_to_next_clip']=['EVENT_4'];self.assertNotIn('unfinished_events',codes(p))
 def test_approved_intentional_repetition_is_allowed(self):
  p=fixture();p['shots'][0]['actions'][0]['occurrences']=3;self.assertIn('unapproved_action_repeat',codes(p));p['shots'][0]['actions'][0]['repeat_approval']={'approved_by':'user','evidence':'Synthetic script explicitly asks for three occurrences.'};self.assertTrue(v.validate(p)['valid'])
 def test_hold_only_shot_does_not_invent_new_motion(self):
  p=fixture();p['shots'][-1]['actions']=[];p['shots'][-1]['hold_states']={'TEST_OBJECT':{'step':3}};p['expected_final_states']={'TEST_OBJECT':{'step':3}};self.assertTrue(v.validate(p)['valid'])
 def test_completed_state_held_wrongly_is_detected(self):
  p=fixture();p['shots'][-1]['hold_states']={'TEST_OBJECT':{'step':0}};self.assertIn('state_reset',codes(p))
 def test_pending_audio_method_is_not_silently_native(self):
  p=fixture();voice=add_voice(p);del voice['generation_mode'];self.assertIn('missing_voice_delivery_choice',codes(p))
 def test_native_description_is_not_verified_voice_lock(self):
  p=fixture();add_voice(p)['strict_identity_required']=True;self.assertIn('native_cannot_verify_identity_lock',codes(p))
 def test_reference_not_connected_is_rejected(self):
  p=fixture();voice=add_voice(p);voice['generation_mode']='audio_reference';voice['reference_audio']={'asset':'fixture.wav','connected':False,'socket':'ref_audio_0'};self.assertIn('unconnected_voice_reference',codes(p))
 def test_false_accepted_voice_claim_is_rejected(self):
  p=fixture();add_voice(p)['verification']={'status':'accepted'};self.assertIn('false_voice_verification',codes(p))
 def test_external_voice_needs_delivery_plan(self):
  p=fixture();voice=add_voice(p);voice['generation_mode']='external_voiceover';self.assertIn('missing_external_audio_plan',codes(p));voice['delivery_plan']='Synthetic externally rendered audio is composited in the approved editor.';self.assertTrue(v.validate(p)['valid'])
 def test_sentence_cannot_restart_at_every_cut(self):
  p=fixture();add_voice(p);second=copy.deepcopy(p['audio']['dialogue'][0]);second.update(utterance_id='LINE_2',start_s=2,end_s=3);p['audio']['dialogue'].append(second);self.assertIn('repeated_dialogue',codes(p))
 def test_reusing_same_utterance_id_twice_rejected(self):
  p=fixture();add_voice(p);p['audio']['dialogue'].append(copy.deepcopy(p['audio']['dialogue'][0]));self.assertIn('duplicate_utterance_id',codes(p))
 def test_spoken_time_over_budget_rejected(self):
  p=fixture();add_voice(p);p['audio']['dialogue'][0]['timing_check']['duration_s']=2;self.assertIn('speech_over_budget',codes(p))
 def test_number_pronunciation_not_silently_rewritten(self):
  p=fixture();add_voice(p);p['audio']['dialogue'][0]['spoken_text']='Other pronunciation fixture.';self.assertIn('unapproved_spoken_text',codes(p))
 def test_approved_spoken_text_can_replace_display_text_without_duplicate_utterance(self):
  p=fixture();add_voice(p);line=p['audio']['dialogue'][0];line['spoken_text']='Câu đọc kiểm thử.';line['pronunciation_approval']={'approved_by':'user','evidence':'Synthetic approved pronunciation.'};p['video_prompt_en']=p['video_prompt_en'].replace(line['text'],line['spoken_text']);self.assertTrue(v.validate(p)['valid'])
 def test_legacy_timestamp_labels_detected_without_header_double_count(self):
  text='Read SHOT 001, SHOT 002 once each.\n00.0–01.5s | SHOT 001: fixture\n01.5–03.0s | SHOT 002: fixture';self.assertEqual(a.shot_labels(text),['1','2'])

if __name__=='__main__':unittest.main(verbosity=2)
