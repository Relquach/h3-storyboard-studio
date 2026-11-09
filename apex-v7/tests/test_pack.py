import copy,hashlib,importlib.util,io,json,pathlib,tempfile,unittest,urllib.error,zipfile
from unittest.mock import patch
ROOT=pathlib.Path(__file__).resolve().parents[1]
def module(name,path):
 spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
ins=module('apex_install',ROOT/'scripts/install.py');hand=module('apex_hand',ROOT/'skill/minimax-h3-film/scripts/apex_handoff.py')
class PackTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.t=pathlib.Path(self.tmp.name);self.w=json.loads((ROOT/'workflows/02_APEX_V7_3D_LTX_1080_DOC.json').read_text());self.man=json.loads((ROOT/'manifest.json').read_text())
 def test_source_unchanged(self):self.assertEqual(hashlib.sha256((ROOT/'source/Apex_H3_v7_original.json').read_bytes()).hexdigest(),self.man['source_sha256'])
 def test_pins_and_sizes(self):
  for m in self.man['models']:
   self.assertRegex(m['revision'],r'^[0-9a-f]{40}$');self.assertRegex(m['sha256'],r'^[0-9a-f]{64}$');self.assertGreater(m['bytes'],0)
  for p in self.man['nodes']:self.assertEqual(ins.dl.sha256(ROOT/'vendor'/p['archive']),p['sha256'])
 def test_all_root_links_consistent(self):
  for p in json.loads((ROOT/'profiles.json').read_text()):
   w=json.loads((ROOT/'workflows'/p['file']).read_text());ns={n['id']:n for n in w['nodes']};seen=set()
   for lid,src,ss,dst,ds,t in w['links']:
    self.assertNotIn(lid,seen);seen.add(lid);self.assertIn(lid,ns[src]['outputs'][ss]['links']);self.assertEqual(ns[dst]['inputs'][ds]['link'],lid)
 def test_real_four_reference_slots(self):self.assertEqual([x['loader'] for x in hand.slots(self.w)],[7330,9408,9409,9413]);self.assertEqual(sum(x['enabled'] for x in hand.slots(self.w)),1)
 def test_pending_no_prompt(self):
  p=json.loads((ROOT/'skill/minimax-h3-film/examples/apex-pending.plan.json').read_text())
  with self.assertRaisesRegex(ValueError,'duyệt'):hand.compile_plan(p,self.w)
 def approved(self):
  p=json.loads((ROOT/'skill/minimax-h3-film/examples/apex-pending.plan.json').read_text());p['storyboard_revision']='SYNTHETIC_TEST';p['storyboard_review']={'status':'approved','approved_by':'user','approved_revision':'SYNTHETIC_TEST','evidence':'SYNTHETIC UNIT TEST ONLY'};p['video_prompt_template']='[SHOT 1] {{start:SHOT 1}}–{{end:SHOT 1}} {{ref:STORYBOARD}}';return p
 def test_stale_approval(self):
  p=self.approved();p['storyboard_revision']='changed'
  with self.assertRaisesRegex(ValueError,'revision'):hand.compile_plan(p,self.w)
 def test_compact_numbers_with_gap(self):
  p=self.approved();p['assets'] +=[{'id':'ENV_01','loader':9409,'enabled':True,'file':'TEST_ONLY.png','description_en':'synthetic environment'}];p['video_prompt_template']+=' {{ref:ENV_01}}';r=hand.compile_plan(p,self.w);self.assertIn('<Picture 2>',r['prompt']);self.assertNotIn('<Picture 3>',r['prompt']);self.assertTrue(r['ui_actions_required']);self.assertEqual(r['mapping'][1]['desired_enabled'],False)
 def test_phantom_ref_rejected(self):
  p=self.approved();p['video_prompt_template']+=' {{ref:CHAR_01}}'
  with self.assertRaises(ValueError):hand.compile_plan(p,self.w)
 def test_unwired_loader_rejected(self):
  p=self.approved();p['assets'].append({'id':'CHAR_01','loader':999,'file':'test','description_en':'x'})
  with self.assertRaisesRegex(ValueError,'nối thật'):hand.compile_plan(p,self.w)
 def test_timing(self):
  self.assertEqual([hand.frames(x) for x in [5,10,15]],[124,243,362])
  for t in [False,float('nan'),0,31]:
   with self.assertRaises(ValueError):hand.frames(t)
 def test_shot_sum_mismatch(self):
  p=self.approved();p['shots'][0]['seconds']=4
  with self.assertRaisesRegex(ValueError,'thời lượng'):hand.compile_plan(p,self.w)
 def test_llm_rewrite_not_accepted(self):
  p=self.approved();edge=next(l for l in self.w['links'] if l[3]==136 and l[4]==10);edge[1]=7232
  with self.assertRaisesRegex(ValueError,'LLM'):hand.compile_plan(p,self.w)
 def test_fake_approval_not_accepted(self):
  p=self.approved();p['storyboard_review']['approved_by']='assistant'
  with self.assertRaises(ValueError):hand.compile_plan(p,self.w)
 def test_portable_root_inner_and_comfy(self):
  p=self.t/'outer/ComfyUI_windows_portable';(p/'python_embeded').mkdir(parents=True);(p/'ComfyUI').mkdir();(p/'python_embeded/python.exe').touch();(p/'ComfyUI/main.py').touch()
  for q in [p,p.parent,p/'ComfyUI']:self.assertEqual(ins.portable_path(q),p)
  with self.assertRaises(ValueError):ins.portable_path(self.t/'not-a-folder.json')
 def test_schema_old_new(self):
  (self.t/'comfy_extras').mkdir();src=self.t/'comfy_extras/nodes_video.py'
  for has in [False,True]:
   src.write_text('chroma_subsampling' if has else 'codec');w=ins.adapt_video_schema(copy.deepcopy(self.w),self.t)
   for g in w['definitions']['subgraphs']:
    for n in g['nodes']:
     if n['type']=='CreateVideo':self.assertEqual(len(n['widgets_values']),5 if has else 4);self.assertEqual(n['widgets_values'][-1],'none')
 def test_schema_reads_default_and_field_order(self):
  (self.t/'comfy_extras').mkdir();(self.t/'comfy_extras/nodes_video.py').write_text("class CreateVideo:\n def define_schema():\n  return [io.Float.Input('fps'), io.Combo.Input('bit_depth'), io.Combo.Input('color_space'), io.Combo.Input('codec'), io.Combo.Input('chroma_subsampling',options=['4:2:0','4:4:4'],default='4:2:0')]\n")
  w=ins.adapt_video_schema(copy.deepcopy(self.w),self.t)
  for g in w['definitions']['subgraphs']:
   for n in g['nodes']:
    if n['type']=='CreateVideo':self.assertEqual(n['widgets_values'],[24,8,'sRGB','none','4:2:0'])
 def test_extra_model_paths_and_nested_name(self):
  c=self.t/'ComfyUI';c.mkdir();extra=self.t/'shared';f=extra/'loras/nested/test.safetensors';f.parent.mkdir(parents=True);f.write_bytes(b'weights')
  (c/'extra_model_paths.yaml').write_text('shared:\n  base_path: '+str(extra)+'\n  loras: loras\n')
  m={'category':'loras','destination':'test.safetensors','bytes':7,'sha256':hashlib.sha256(b'weights').hexdigest()};path,name=ins.locate(c,m,verify=True);self.assertEqual(name,'nested/test.safetensors')
 def test_wrong_existing_model_not_overwritten(self):
  f=self.t/'models/loras/test.safetensors';f.parent.mkdir(parents=True);f.write_bytes(b'bad')
  with self.assertRaises(RuntimeError):ins.locate(self.t,{'category':'loras','destination':f.name,'bytes':2},verify=True)
  self.assertEqual(f.read_bytes(),b'bad')
 def archive(self,name):
  p=self.t/'node.zip'
  with zipfile.ZipFile(p,'w') as z:z.writestr(name,'x')
  return p
 def test_zip_traversal_rejected(self):
  for name in ['../escape','/escape','root/../../escape','root\\escape','C:/escape']:
   with self.assertRaises(ValueError):ins.safe_extract(self.archive(name),self.t/'extract')
 def test_zip_symlink_rejected(self):
  p=self.t/'symlink.zip'
  with zipfile.ZipFile(p,'w') as z:
   i=zipfile.ZipInfo('root/link');i.create_system=3;i.external_attr=(0o120777<<16);z.writestr(i,'../../x')
  with self.assertRaises(ValueError):ins.safe_extract(p,self.t/'extract')
 def test_node_backup_idempotence(self):
  c=self.t/'ComfyUI';(c/'user/ApexV7').mkdir(parents=True);pack=self.man['nodes'][0];target=c/'custom_nodes'/pack['folder'];target.mkdir(parents=True);(target/'__init__.py').write_text('# existing user revision')
  ins.install_node(c,pack);backups=list((c/'user/ApexV7/backups').iterdir());self.assertEqual(len(backups),1);self.assertEqual((backups[0]/'__init__.py').read_text(),'# existing user revision');ins.install_node(c,pack);self.assertEqual(len(list((c/'user/ApexV7/backups').iterdir())),1)
 def test_failed_node_copy_restores_backup(self):
  c=self.t/'ComfyUI';(c/'user/ApexV7').mkdir(parents=True);pack=self.man['nodes'][0];target=c/'custom_nodes'/pack['folder'];target.mkdir(parents=True);(target/'__init__.py').write_text('# user original')
  with patch.object(ins.shutil,'copytree',side_effect=OSError('synthetic copy failure')):
   with self.assertRaises(OSError):ins.install_node(c,pack)
  self.assertEqual((target/'__init__.py').read_text(),'# user original')

 def test_rewrite_names_all_widgets(self):
  m=self.man['models'][0];w=ins.rewrite_names(self.w,{m['id']:'nested/'+m['destination']},self.man);n=next(n for n in w['nodes'] if n['id']==127);self.assertEqual(n['widgets_values'][0],'nested/'+m['destination'])
class Response(io.BytesIO):
 def __init__(self,body,status=200,headers=None):super().__init__(body);self.status=status;self.headers=headers or {}
class DownloadTests(unittest.TestCase):
 def setUp(self):self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.dest=pathlib.Path(self.tmp.name)/'file.safetensors';self.payload=b'valid-test-payload';self.sha=hashlib.sha256(self.payload).hexdigest()
 def test_download_hash_verified(self):
  with patch.object(ins.dl.urllib.request,'urlopen',return_value=Response(self.payload)):ins.dl.download('https://example.invalid/model',self.dest,len(self.payload),self.sha)
  self.assertEqual(self.dest.read_bytes(),self.payload)
 def test_html_not_installed_as_model(self):
  with patch.object(ins.dl.urllib.request,'urlopen',return_value=Response(b'<!DOCTYPE HTML>')):
   with self.assertRaises(RuntimeError):ins.dl.download('https://example.invalid/model',self.dest,len(self.payload),self.sha)
  self.assertFalse(self.dest.exists())
 def test_resume_range(self):
  self.dest.with_name(self.dest.name+'.part').write_bytes(self.payload[:5])
  def urlopen(req,timeout):self.assertEqual(req.get_header('Range'),'bytes=5-');return Response(self.payload[5:],206,{'Content-Range':'bytes 5-17/18'})
  with patch.object(ins.dl.urllib.request,'urlopen',side_effect=urlopen):ins.dl.download('https://example.invalid/model',self.dest,len(self.payload),self.sha)
  self.assertEqual(self.dest.read_bytes(),self.payload)
 def test_server_ignores_range_restarts(self):
  self.dest.with_name(self.dest.name+'.part').write_bytes(self.payload[:5])
  with patch.object(ins.dl.urllib.request,'urlopen',return_value=Response(self.payload)):ins.dl.download('https://example.invalid/model',self.dest,len(self.payload),self.sha)
  self.assertEqual(self.dest.read_bytes(),self.payload)
 def test_full_corrupt_part_quarantined(self):
  self.dest.with_name(self.dest.name+'.part').write_bytes(b'x'*len(self.payload))
  with self.assertRaisesRegex(RuntimeError,'SHA256'):ins.dl.download('https://example.invalid/model',self.dest,len(self.payload),self.sha)
  self.assertFalse(self.dest.exists());self.assertTrue(list(self.dest.parent.glob('*.corrupt-*')))
if __name__=='__main__':unittest.main()
