import copy,hashlib,importlib.util,io,json,pathlib,tempfile,unittest,zipfile
from unittest.mock import patch
ROOT=pathlib.Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('openh3_install',ROOT/'scripts/install.py');ins=importlib.util.module_from_spec(spec);spec.loader.exec_module(ins)
class InstallTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.t=pathlib.Path(self.tmp.name);self.man=json.loads((ROOT/'manifest.json').read_text())
 def model(self,data=b'fixture model'):
  return {'id':'x','category':'loras','destination':'expected.safetensors','aliases':['alias.safetensors'],'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()}
 def test_original_exact_bytes(self):
  data=ins.original_bytes(self.man);self.assertEqual(len(data),36366);self.assertEqual(hashlib.sha256(data).hexdigest(),'77801992727a09a22547b44f0b70b985e9472820da2e21941a87cf778d8e5973')
 def test_copy_is_identical_and_preserves_changed_destination_backup(self):
  p=ins.copy_original_workflow(self.t,self.man);original=p.read_bytes();p.write_bytes(b'user edits');ins.copy_original_workflow(self.t,self.man);self.assertEqual(p.read_bytes(),original);self.assertEqual(next((self.t/'user/OpenH3_Original/backups').rglob('*.json')).read_bytes(),b'user edits')
 def test_rerun_copy_does_not_reformat(self):
  p=ins.copy_original_workflow(self.t,self.man);before=p.read_bytes();ins.copy_original_workflow(self.t,self.man);self.assertEqual(before,p.read_bytes());self.assertFalse((self.t/'user/OpenH3_Original/backups').exists())
 def test_modified_source_rejected(self):
  with patch.object(ins,'ROOT',self.t):
   (self.t/'workflows').mkdir();(self.t/'workflows'/self.man['workflow']).write_bytes(ins.ROOT.as_posix().encode())
   with self.assertRaises(RuntimeError):ins.original_bytes(self.man)
 def test_manifest_model_names_match_original_widgets(self):
  w=json.loads(ins.original_bytes(self.man));n={x['id']:x for x in w['nodes']};by={m['id']:m for m in self.man['models']}
  fields=[(4,0,'video_vae'),(7,0,'audio_vae'),(30,0,'latent_upscale'),(12,0,'encoder'),(13,0,'singularity_v2'),(13,1,'regenerate_lora'),(13,2,'curve_branches')]
  for nid,slot,mid in fields:self.assertEqual(n[nid]['widgets_values'][slot],by[mid]['destination'])
  self.assertEqual(n[6]['widgets_values'],[2560,1440]);self.assertEqual(n[22]['widgets_values'],['2']);self.assertEqual(n[28]['mode'],2);self.assertEqual(n[29]['mode'],2)
 def test_pins_and_vendor_checksums(self):
  for m in self.man['models']:self.assertRegex(m['revision'],r'^[0-9a-f]{40}$');self.assertRegex(m['sha256'],r'^[0-9a-f]{64}$')
  for m in self.man['nodes']:self.assertEqual(ins.dl.sha256(ROOT/'vendor'/m['archive']),m['sha256'])
 def test_portable_folder_selection(self):
  p=self.t/'outer/ComfyUI_windows_portable';(p/'python_embeded').mkdir(parents=True);(p/'ComfyUI').mkdir();(p/'python_embeded/python.exe').touch();(p/'ComfyUI/main.py').touch()
  for x in [p,p.parent,p/'ComfyUI']:self.assertEqual(ins.portable_path(x),p)
  with self.assertRaises(ValueError):ins.portable_path(self.t/'workflow.json')
 def test_core_old_missing_native_features(self):
  (self.t/'nodes.py').touch();f=ins.core_features(self.t,self.man);self.assertFalse(f['MiniMaxH3LatentUpscaleWithModel']);self.assertFalse(f['native_h3_chunked_io'])
  with self.assertRaisesRegex(RuntimeError,'update_comfyui'):ins.preflight(self.t,self.man)
 def test_direct_model_hash_and_existing_wrong_model_not_overwritten(self):
  m=self.model();p=self.t/'models/loras'/m['destination'];p.parent.mkdir(parents=True);p.write_bytes(b'fixture model');self.assertEqual(ins.direct_model(self.t,m,True),p);p.write_bytes(b'wrong model!!')
  with self.assertRaises(RuntimeError):ins.direct_model(self.t,m,True)
  self.assertEqual(p.read_bytes(),b'wrong model!!')
 def test_nested_canonical_model_can_be_aliased_without_changing_workflow(self):
  m=self.model();src=self.t/'models/loras/nested/alias.safetensors';src.parent.mkdir(parents=True);src.write_bytes(b'fixture model');self.assertIsNone(ins.direct_model(self.t,m,True));self.assertEqual(ins.reusable_model(self.t,m),src);dst=self.t/'models/loras'/m['destination'];kind=ins.make_model_alias(src,dst,m);self.assertEqual(kind,'hardlink');self.assertEqual(src.stat().st_ino,dst.stat().st_ino);self.assertEqual(dst.read_bytes(),src.read_bytes());self.assertEqual(ins.original_bytes(self.man),(ROOT/'workflows'/self.man['workflow']).read_bytes())
 def test_alias_wrong_content_not_reused(self):
  m=self.model();f=self.t/'models/loras/nested/alias.safetensors';f.parent.mkdir(parents=True);f.write_bytes(b'x'*m['bytes']);self.assertIsNone(ins.reusable_model(self.t,m))
 def test_existing_alias_destination_not_overwritten(self):
  m=self.model();src=self.t/'alias.safetensors';src.write_bytes(b'fixture model');dst=self.t/'models/loras'/m['destination'];dst.parent.mkdir(parents=True);dst.write_bytes(b'wrong')
  with self.assertRaises(RuntimeError):ins.make_model_alias(src,dst,m)
  self.assertEqual(dst.read_bytes(),b'wrong')
 def test_cross_volume_alias_copy(self):
  m=self.model();src=self.t/'alias.safetensors';src.write_bytes(b'fixture model');dst=self.t/'models/loras'/m['destination'];real=ins.os.link
  def link(a,b):
   if pathlib.Path(a)==src:raise OSError('synthetic cross-volume link')
   return real(a,b)
  with patch.object(ins.os,'link',side_effect=link):kind=ins.make_model_alias(src,dst,m)
  self.assertEqual(kind,'copy');self.assertEqual(dst.read_bytes(),src.read_bytes());self.assertTrue(src.exists())
 def test_extra_model_paths_root_direct_name(self):
  c=self.t/'ComfyUI';c.mkdir();shared=self.t/'shared';(shared/'loras').mkdir(parents=True);m=self.model();f=shared/'loras'/m['destination'];f.write_bytes(b'fixture model');(c/'extra_model_paths.yaml').write_text('shared:\n  base_path: '+str(shared)+'\n  loras: loras\n');self.assertEqual(ins.direct_model(c,m,True),f)
 def test_zip_traversal_and_symlink_rejected(self):
  for name in ['../escape','/escape','root/../../escape','root\\escape','C:/escape']:
   archive=self.t/'bad.zip'
   with zipfile.ZipFile(archive,'w') as z:z.writestr(name,'x')
   with self.assertRaises(ValueError):ins.safe_extract(archive,self.t/'extract')
  with zipfile.ZipFile(archive,'w') as z:
   i=zipfile.ZipInfo('root/link');i.create_system=3;i.external_attr=0o120777<<16;z.writestr(i,'../x')
  with self.assertRaises(ValueError):ins.safe_extract(archive,self.t/'extract')
 def test_node_backup_idempotence(self):
  c=self.t/'ComfyUI';(c/'user/OpenH3_Original').mkdir(parents=True);p=self.man['nodes'][0];dest=c/'custom_nodes'/p['folder'];dest.mkdir(parents=True);(dest/'__init__.py').write_text('# user previous')
  ins.install_node(c,p);self.assertEqual(len(list((c/'user/OpenH3_Original/backups').iterdir())),1);ins.install_node(c,p);self.assertEqual(len(list((c/'user/OpenH3_Original/backups').iterdir())),1)
 def test_failed_copy_restores_node(self):
  c=self.t/'ComfyUI';(c/'user/OpenH3_Original').mkdir(parents=True);p=self.man['nodes'][0];dest=c/'custom_nodes'/p['folder'];dest.mkdir(parents=True);(dest/'__init__.py').write_text('# previous')
  with patch.object(ins.shutil,'copytree',side_effect=OSError('copy failure')):
   with self.assertRaises(OSError):ins.install_node(c,p)
  self.assertEqual((dest/'__init__.py').read_text(),'# previous')
 def test_combo_options_both_schemas(self):
  for field in [[['x','y'],{}],['COMBO',{'options':['x','y']}]]:self.assertEqual(ins.combo_options({'input':{'required':{'model':field}}},'model'),['x','y'])
if __name__=='__main__':unittest.main()
