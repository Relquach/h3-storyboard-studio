import hashlib,importlib.util,io,json,pathlib,subprocess,sys,tempfile,unittest,zipfile
from unittest.mock import patch
ROOT=pathlib.Path(__file__).resolve().parents[1];sys.path.append(str(ROOT/'scripts'))
import install_missing as fix
import downloads
class MissingFixTests(unittest.TestCase):
 def portable(self,root):
  p=pathlib.Path(root)/'ComfyUI_windows_portable';(p/'python_embeded').mkdir(parents=True);(p/'python_embeded/python.exe').touch();(p/'ComfyUI').mkdir();(p/'ComfyUI/main.py').write_text('original core')
  return p
 def archive(self,path):
  with zipfile.ZipFile(path,'w') as z:
   for name in ['__init__.py','nodes/node_monitor.py','nodes/node_run_timer.py']:z.writestr('repo/'+name,'# fixture')
  return path
 def model(self,data=b'model'):
  return {'destination':'vae/a.safetensors','bytes':len(data),'sha256':hashlib.sha256(data).hexdigest(),'file':'a.safetensors','repo':'fixture/repo','revision':'a'*40}
 def test_portable_root_accepts_nested_and_comfy_selection(self):
  with tempfile.TemporaryDirectory() as d:
   p=self.portable(d);self.assertEqual(fix.portable_root(p/'ComfyUI'),p);self.assertEqual(fix.portable_root(p.parent),p)
 def test_bad_folder_rejected(self):
  with tempfile.TemporaryDirectory() as d:
   with self.assertRaises(ValueError):fix.portable_root(d)
 def test_archive_traversal_refused(self):
  with tempfile.TemporaryDirectory() as d:
   z=pathlib.Path(d)/'bad.zip'
   with zipfile.ZipFile(z,'w') as f:f.writestr('..\\outside.py','bad')
   with self.assertRaises(ValueError):fix.extract_repo(z,pathlib.Path(d)/'out')
 def test_pack_backup_outside_custom_nodes_and_idempotent(self):
  with tempfile.TemporaryDirectory() as d:
   root=pathlib.Path(d);p=self.portable(root);z=self.archive(root/'pack.zip');target=p/'ComfyUI/custom_nodes/ComfyUI-Pixaroma';target.mkdir(parents=True);(target/'__init__.py').write_text('user old')
   fix.install_pack(p/'ComfyUI',z)
   backup=list((p/'ComfyUI/user/h3_missing_fix/backups').glob('*'));self.assertEqual(len(backup),1);self.assertEqual((backup[0]/'__init__.py').read_text(),'user old')
   fix.install_pack(p/'ComfyUI',z);self.assertEqual(len(list((p/'ComfyUI/user/h3_missing_fix/backups').glob('*'))),1)
 def test_failed_pack_move_restores_old(self):
  with tempfile.TemporaryDirectory() as d:
   root=pathlib.Path(d);p=self.portable(root);z=self.archive(root/'pack.zip');target=p/'ComfyUI/custom_nodes/ComfyUI-Pixaroma';target.mkdir(parents=True);(target/'__init__.py').write_text('keep')
   with patch.object(fix.shutil,'move',side_effect=OSError('fixture fail')):
    with self.assertRaises(OSError):fix.install_pack(p/'ComfyUI',z)
   self.assertEqual((target/'__init__.py').read_text(),'keep')
 def test_model_reused_by_hash_no_download(self):
  with tempfile.TemporaryDirectory() as d:
   root=pathlib.Path(d);p=root/'models/vae/a.safetensors';p.parent.mkdir(parents=True);p.write_bytes(b'model');resolved,found=fix.resolve_model(root,self.model());self.assertTrue(found);self.assertEqual(resolved,p)
 def test_wrong_existing_model_preserved(self):
  with tempfile.TemporaryDirectory() as d:
   root=pathlib.Path(d);p=root/'models/vae/a.safetensors';p.parent.mkdir(parents=True);p.write_bytes(b'keep')
   with self.assertRaises(RuntimeError):fix.resolve_model(root,self.model())
   self.assertEqual(p.read_bytes(),b'keep')
 def test_shared_model_reused(self):
  try:import yaml
  except ImportError:self.skipTest('PyYAML not installed in test Python')
  with tempfile.TemporaryDirectory() as d:
   root=pathlib.Path(d);shared=root/'shared';shared.mkdir();(shared/'a.safetensors').write_bytes(b'model')
   (root/'extra_model_paths.yaml').write_text('shared:\n  base_path: shared\n  vae: .\n')
   resolved,found=fix.resolve_model(root,self.model());self.assertTrue(found);self.assertEqual(resolved,shared/'a.safetensors')
 def test_dependency_missing_only_does_not_upgrade_torch(self):
  with patch.object(fix.importlib.util,'find_spec',return_value=None),patch.object(fix.subprocess,'run') as run:
   run.return_value.returncode=0;run.return_value.stdout='fixture';fix.install_dependencies();cmd=run.call_args.args[0]
   self.assertIn('--no-deps',cmd);self.assertNotIn('--upgrade',cmd);self.assertFalse(any(arg.startswith('torch') for arg in cmd))
 def test_existing_dependency_no_pip_call(self):
  with patch.object(fix.importlib.util,'find_spec',return_value=object()),patch.object(fix.subprocess,'run') as run:
   fix.install_dependencies();run.assert_not_called()
 def test_download_resumes_and_validates(self):
  with tempfile.TemporaryDirectory() as d:
   p=pathlib.Path(d)/'model';p.with_name('model.part').write_bytes(b'abc');r=io.BytesIO(b'def');r.status=206;r.headers={'Content-Range':'bytes 3-5/6'}
   with patch('urllib.request.urlopen',return_value=r):downloads.download('https://example.invalid',p,6,hashlib.sha256(b'abcdef').hexdigest())
   self.assertEqual(p.read_bytes(),b'abcdef')
 def test_corrupt_payload_not_promoted(self):
  with tempfile.TemporaryDirectory() as d:
   p=pathlib.Path(d)/'model';r=io.BytesIO(b'bad');r.status=200;r.headers={}
   with patch('urllib.request.urlopen',return_value=r):
    with self.assertRaisesRegex(RuntimeError,'SHA256'):downloads.download('https://example.invalid',p,3,'0'*64)
   self.assertFalse(p.exists());self.assertEqual(len(list(pathlib.Path(d).glob('*.corrupt-*'))),1)
 def test_isolated_python_can_import_sibling_without_stdlib_shadow(self):
  r=subprocess.run([sys.executable,'-I',str(ROOT/'scripts/install_missing.py'),'--help'],capture_output=True,text=True)
  self.assertEqual(r.returncode,0,r.stderr);self.assertIn('--portable',r.stdout)
 def test_full_fixture_install_keeps_workflow_and_core(self):
  with tempfile.TemporaryDirectory() as d:
   root=pathlib.Path(d);p=self.portable(root);comfy=p/'ComfyUI';workflow=comfy/'original.json';workflow.write_text('untouched workflow');pack=self.archive(root/'pack.zip');bundle=root/'bundle';(bundle/'reports').mkdir(parents=True)
   model=self.model();manifest={'node_pack':{**fix.MANIFEST['node_pack'],'archive_bytes':pack.stat().st_size,'archive_sha256':hashlib.sha256(pack.read_bytes()).hexdigest()},'models':[model]}
   def download_fixture(url,dest,*args):
    pathlib.Path(dest).parent.mkdir(parents=True,exist_ok=True)
    pathlib.Path(dest).write_bytes(pack.read_bytes() if str(dest).endswith('.zip') else b'model')
   with patch.object(fix,'ROOT',bundle),patch.object(fix,'MANIFEST',manifest),patch.object(fix,'download',side_effect=download_fixture),patch.object(fix,'install_dependencies'):
    fix.run_install(p)
   self.assertEqual(workflow.read_text(),'untouched workflow');self.assertEqual((comfy/'main.py').read_text(),'original core');self.assertEqual((comfy/'models/vae/a.safetensors').read_bytes(),b'model');self.assertTrue((bundle/'reports/installed.json').exists())
if __name__=='__main__':unittest.main()
