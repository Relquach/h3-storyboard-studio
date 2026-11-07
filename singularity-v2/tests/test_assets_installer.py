import unittest,sys,pathlib,json,tempfile,zipfile,copy
from unittest.mock import patch
ROOT=pathlib.Path(__file__).resolve().parents[1];sys.path.append(str(ROOT/'scripts'))
import assets,build,setup_studio
class AssetTests(unittest.TestCase):
 def setUp(self):self.p=json.loads((ROOT/'examples/lan-15s.project.json').read_text())
 def test_whole_grid_and_sheet_have_same_prompt_and_wires(self):
  w,active=assets.wire_assets(build.template(),self.p,['grid.png','lan.png']);nodes={n['id']:n for n in w['nodes']};text=nodes[70]['widgets_values'][0]
  self.assertIn('<Picture 1>: STORYBOARD',text);self.assertIn('<Picture 2>: CHAR_01',text);self.assertNotIn('<Asset:',text)
  links=[l for l in w['links'] if l[3]==26 and l[5]=='IMAGE']
  self.assertEqual([nodes[l[1]]['widgets_values'][0] for l in links],['grid.png','lan.png'])
  self.assertEqual([nodes[26]['inputs'][l[4]]['name'] for l in links],['ref_images.ref_image_0','ref_images.ref_image_1'])
 def test_no_sheet_storyboard_only_does_not_leave_picture_2(self):
  self.p['assets'][1]['enabled']=False;prompt,active=assets.compile_assets(self.p)
  self.assertEqual(len(active),1);self.assertNotIn('<Picture 2>',prompt);self.assertIn('no separate reference supplied',prompt)
  w,_=assets.wire_assets(build.template(),self.p,['grid.png']);nodes={n['id']:n for n in w['nodes']}
  self.assertEqual(sum(n['type']=='LoadImage' for n in nodes.values()),1)
 def test_disabled_middle_never_swaps_later_asset(self):
  self.p['assets'].insert(1,{'id':'PROP_01','role':'prop','enabled':False,'description':'A wooden sword'})
  self.p['assets'][-1]['enabled']=True;self.p['video_prompt']+=' Sword <Asset:PROP_01>, field <Asset:ENV_01>.'
  prompt,active=assets.compile_assets(self.p)
  self.assertEqual([a['id'] for a in active],['STORYBOARD','CHAR_01','ENV_01']);self.assertIn('field <Picture 3>',prompt)
 def test_unknown_asset_fails_before_file_copy(self):
  self.p['video_prompt']='<Asset:CHAR_99>'
  with self.assertRaisesRegex(ValueError,'không khai báo'):assets.compile_assets(self.p)
 def test_raw_picture_numbers_rejected_at_preparation(self):
  self.p['video_prompt']='Face <Picture 2>'
  with self.assertRaisesRegex(ValueError,'<Asset:ID>'):assets.compile_assets(self.p)
 def test_duplicate_id_rejected(self):
  self.p['assets'].append(self.p['assets'][1])
  with self.assertRaisesRegex(ValueError,'Trùng'):assets.compile_assets(self.p)
 def test_storyboard_required(self):
  self.p['assets'][0]['enabled']=False
  with self.assertRaisesRegex(ValueError,'STORYBOARD'):assets.compile_assets(self.p)
 def test_max_images(self):
  self.p['assets']+=[{'id':'A'+str(i),'enabled':True,'role':'prop','description':'object'} for i in range(8)]
  with self.assertRaisesRegex(ValueError,'9 ảnh'):assets.compile_assets(self.p)
 def test_duration_bound_and_alignment(self):
  self.assertEqual(assets.frame_count(15),362);self.assertEqual(assets.frame_count(5),124)
  for seconds in [True,float('nan'),float('inf'),30,0,-1]:
   with self.assertRaises(ValueError):assets.frame_count(seconds)
 def test_copy_only_enabled_real_files(self):
  with tempfile.TemporaryDirectory() as d:
   root=pathlib.Path(d);src=root/'source.png';__import__('PIL.Image',fromlist=['Image']).new('RGB',(32,32),'white').save(src)
   self.p['assets'][0]['file']=str(src);self.p['assets'][1]['file']=str(src);self.p['assets'][2]['file']='missing-ignored.png'
   out=assets.prepare(build.template(),self.p,root/'ComfyUI',root/'ready.json');self.assertTrue(out.exists())
   mapping=json.loads(out.with_suffix('.mapping.json').read_text());self.assertEqual([x['picture'] for x in mapping],[1,2]);self.assertTrue(src.exists())
 def test_ref_area_and_draft_latent_remain_separate(self):
  w=build.template();nodes={n['id']:n for n in w['nodes']}
  self.assertEqual(nodes[26]['widgets_values'][1:3],[992,1792]);self.assertTrue(any(l[1]==159 and l[3]==61 for l in w['links']))
  self.assertEqual(nodes[25]['type'],'ResolutionSelector')
 def test_core_nodes_only_no_old_wrapper(self):
  w=build.template();self.assertFalse(any(n['type'].startswith('H3Studio') for n in w['nodes']))
  nodes={n['id']:n for n in w['nodes']};self.assertEqual(nodes[134]['mode'],4);self.assertEqual(nodes[11]['mode'],4);self.assertEqual(nodes[12]['mode'],4)
 def test_take_preserved_for_upscale_not_current_prompt(self):
  w=build.template();self.assertTrue(any(l[1]==124 and l[2]==1 and l[3]==120 for l in w['links']))
  self.assertTrue(any(l[1]==124 and l[2]==0 and l[3]==120 for l in w['links']))
 def test_links_complete_both_templates(self):
  for p in (ROOT/'workflows').glob('*.json'):
   if p.name=='template.json':continue
   w=json.loads(p.read_text());assets.normalize_links(w)
class InstallerTests(unittest.TestCase):
 def test_audio_patch_exact_and_idempotent(self):
  src='def fixture():\n                piece = {"samples": comfy.nested_tensor.NestedTensor((chunk_v, chunk_a))}\n                out = sample_piece(piece, cond_i, model, noise, sampler, sigmas, negative, cfg)\n'
  with tempfile.TemporaryDirectory() as d:
   p=pathlib.Path(d)/'nodes.py';p.write_text(src);self.assertEqual(setup_studio.freeze_audio(p),'patched');self.assertEqual(setup_studio.freeze_audio(p),'already-patched')
   self.assertTrue(p.with_suffix('.py.before-audio-freeze').exists());self.assertIn('noise_mask',p.read_text());compile(p.read_text(),str(p),'exec')
 def test_audio_patch_refuses_changed_upstream(self):
  with tempfile.TemporaryDirectory() as d:
   p=pathlib.Path(d)/'nodes.py';p.write_text('unrelated code')
   with self.assertRaisesRegex(RuntimeError,'không khớp'):setup_studio.freeze_audio(p)
   self.assertEqual(p.read_text(),'unrelated code')
 def test_archive_traversal_and_windows_paths(self):
  with tempfile.TemporaryDirectory() as d:
   p=pathlib.Path(d)/'a.zip'
   with zipfile.ZipFile(p,'w') as z:z.writestr('..\\escape','bad')
   with self.assertRaises(ValueError):setup_studio.safe_extract(p,pathlib.Path(d)/'target')
   with zipfile.ZipFile(p,'w') as z:z.writestr('good\\node.py','ok')
   setup_studio.safe_extract(p,pathlib.Path(d)/'target');self.assertEqual((pathlib.Path(d)/'target/good/node.py').read_text(),'ok')
 def test_download_resumes_and_verifies(self):
  import io,hashlib
  from downloads import download
  with tempfile.TemporaryDirectory() as d:
   p=pathlib.Path(d)/'model';p.with_name('model.part').write_bytes(b'abc');response=io.BytesIO(b'def');response.status=206;response.headers={'Content-Range':'bytes 3-5/6'}
   with patch('urllib.request.urlopen',return_value=response):download('https://example.invalid',p,6,hashlib.sha256(b'abcdef').hexdigest())
   self.assertEqual(p.read_bytes(),b'abcdef')
 def test_bad_existing_model_not_overwritten(self):
  from downloads import download
  with tempfile.TemporaryDirectory() as d:
   p=pathlib.Path(d)/'model';p.write_bytes(b'keep')
   with self.assertRaises(RuntimeError):download('https://example.invalid',p,5,'0'*64)
   self.assertEqual(p.read_bytes(),b'keep')
 def test_driver_selection(self):
  from types import SimpleNamespace
  for driver,cuda in [('581.20','cu130'),('576.02','cu128')]:
   with patch('subprocess.run',return_value=SimpleNamespace(stdout=driver)):self.assertEqual(setup_studio.driver_cuda(),cuda)
 def test_all_models_have_pinned_revision_size_hash(self):
  for m in setup_studio.MANIFEST['models']:
   self.assertEqual(len(m['revision']),40);self.assertEqual(len(m['sha256']),64);self.assertGreater(m['bytes'],1000000)
if __name__=='__main__':unittest.main()
