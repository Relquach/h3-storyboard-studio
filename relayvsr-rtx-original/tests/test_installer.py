import contextlib,hashlib,importlib.util,io,json,pathlib,sys,tempfile,unittest,zipfile
from unittest.mock import patch
ROOTS=[pathlib.Path(__file__).resolve().parents[1]]
def load(root):
 spec=importlib.util.spec_from_file_location('installer_'+root.name.replace('-','_'),root/'scripts/install.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
def suite(root):
 m=load(root);manifest=json.loads((root/'manifest.json').read_text());is_relay='Relay' in root.name
 class Tests(unittest.TestCase):
  def setUp(self):
   self.t=tempfile.TemporaryDirectory();self.base=pathlib.Path(self.t.name);self.portable=self.base/'portable';self.comfy=self.portable/'ComfyUI';self.comfy.mkdir(parents=True);(self.comfy/'main.py').touch();(self.portable/'python_embeded').mkdir();(self.portable/'python_embeded/python.exe').touch();(self.comfy/'user/RelayVSR_RTX_Original').mkdir(parents=True);(self.comfy/'comfy_extras').mkdir();(self.comfy/'nodes.py').write_text('\n'.join(manifest['core_required_types']))
  def tearDown(self):self.t.cleanup()
  def fixture(self):
   data=b'verified-small-model';return data,{'category':'vae','destination':'same.safetensors','aliases':[],'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()}
  def test_original_hash(self):self.assertEqual(hashlib.sha256(m.original_bytes(manifest)).hexdigest(),manifest['workflow_sha256'])
  def test_portable_choices(self):
   self.assertEqual(m.portable_path(self.portable),self.portable);self.assertEqual(m.portable_path(self.comfy),self.portable)
   with self.assertRaises(ValueError):m.portable_path(self.base)
  def test_copy_backup_preserves_original(self):
   dest=m.copy_original_workflow(self.comfy,manifest);self.assertEqual(dest.read_bytes(),m.original_bytes(manifest));dest.write_bytes(b'user-edit');m.copy_original_workflow(self.comfy,manifest);backups=list((self.comfy/'user').rglob(manifest['workflow']));self.assertEqual(len(backups),2);self.assertTrue(any(p.read_bytes()==b'user-edit' for p in backups));self.assertEqual(dest.read_bytes(),m.original_bytes(manifest))
  def test_same_name_wrong_model_kept(self):
   data,model=self.fixture();f=self.comfy/'models/vae'/model['destination'];f.parent.mkdir(parents=True);f.write_bytes(b'wrong')
   with self.assertRaises(RuntimeError):m.direct_model(self.comfy,model,True)
   self.assertEqual(f.read_bytes(),b'wrong')
  def test_reuse_subfolder_and_hardlink(self):
   data,model=self.fixture();f=self.comfy/'models/vae/nested'/model['destination'];f.parent.mkdir(parents=True);f.write_bytes(data);self.assertEqual(m.reusable_model(self.comfy,model),f);dest=self.comfy/'models/vae'/model['destination'];self.assertEqual(m.make_model_alias(f,dest,model),'hardlink');self.assertEqual(dest.read_bytes(),data)
  def test_external_model_paths(self):
   data,model=self.fixture();shared=self.base/'shared';shared.mkdir();(shared/model['destination']).write_bytes(data);(self.comfy/'extra_model_paths.yaml').write_text('shared:\n  base_path: '+str(self.base)+'\n  vae: shared\n');self.assertEqual(m.direct_model(self.comfy,model,True),shared/model['destination'])
  def test_verified_local_download(self):
   data,model=self.fixture();src=self.base/'source.bin';src.write_bytes(data);dest=self.base/'download.bin';m.dl.download(src.as_uri(),dest,len(data),model['sha256']);self.assertEqual(dest.read_bytes(),data);m.dl.download(src.as_uri(),dest,len(data),model['sha256'])
  def test_corrupt_download_not_published(self):
   data,model=self.fixture();src=self.base/'source.bin';src.write_bytes(data);dest=self.base/'download.bin'
   with self.assertRaises(RuntimeError):m.dl.download(src.as_uri(),dest,len(data),'0'*64)
   self.assertFalse(dest.exists());self.assertTrue(list(self.base.glob('*.corrupt-*')))
  def test_tampered_source_rejected(self):
   altered=dict(manifest,workflow_sha256='0'*64)
   with self.assertRaises(RuntimeError):m.original_bytes(altered)
  def test_preflight_missing_native_blocks_before_download(self):
   (self.comfy/'nodes.py').write_text('')
   with self.assertRaises(RuntimeError):m.preflight(self.comfy,manifest,True) if is_relay else m.preflight(self.comfy,manifest)
  if is_relay:
   def test_flat_node_archive(self):
    z=self.base/'flat.zip'
    with zipfile.ZipFile(z,'w') as f:f.writestr('__init__.py','x=1')
    self.assertEqual(m.safe_extract(z,self.base/'flat'),self.base/'flat')
   def test_zip_traversal_rejected(self):
    z=self.base/'bad.zip'
    with zipfile.ZipFile(z,'w') as f:f.writestr('../escape.py','x')
    with self.assertRaises(ValueError):m.safe_extract(z,self.base/'extract')
    self.assertFalse((self.base/'escape.py').exists())
   def test_bundled_nodes_hash_extract_and_idempotence(self):
    for pack in manifest['nodes']:
     target=m.install_node(self.comfy,pack);self.assertTrue((target/'__init__.py').is_file());(target/'runtime').mkdir(exist_ok=True);(target/'runtime/keep').write_text('runtime');m.install_node(self.comfy,pack);self.assertEqual((target/'runtime/keep').read_text(),'runtime')
   def test_dlss_update_preserves_runtime(self):
    pack=manifest['nodes'][0];target=m.install_node(self.comfy,pack);(target/'config.json').write_text('{"runtime_dir":"custom"}');(target/'runtime').mkdir();(target/'runtime/keep').write_text('runtime');(target/'__init__.py').write_text('old');m.install_node(self.comfy,pack);self.assertEqual((target/'runtime/keep').read_text(),'runtime');self.assertIn('custom',(target/'config.json').read_text());self.assertTrue(list((self.comfy/'user/RelayVSR_RTX_Original/backups').iterdir()))
   def test_runtime_license_not_autoaccepted(self):
    with patch.object(m,'dlss_runtime_status',side_effect=[{'files_present':False},{'files_present':True}]),patch.object(m.subprocess,'run') as run:
     run.return_value.returncode=0;m.install_runtime(self.comfy,manifest);args=run.call_args.args[0];self.assertIn('--url',args);self.assertEqual(args[args.index('--url')+1],manifest['dlss_runtime']['release_url']);self.assertIn('/v3.0/',args[args.index('--url')+1]);self.assertNotIn('--yes',args);self.assertNotIn('input',run.call_args.kwargs);self.assertNotIn('stdout',run.call_args.kwargs)
   def test_existing_runtime_reused(self):
    with patch.object(m,'dlss_runtime_status',return_value={'files_present':True}),patch.object(m.subprocess,'run') as run:self.assertTrue(m.install_runtime(self.comfy,manifest));run.assert_not_called()
   def test_runtime_decline_does_not_claim_success(self):
    with patch.object(m,'dlss_runtime_status',return_value={'files_present':False}),patch.object(m.subprocess,'run') as run:
     run.return_value.returncode=1
     with self.assertRaises(RuntimeError):m.install_runtime(self.comfy,manifest)
   def test_full_install_blocks_cpu_environment(self):
    with patch.object(m.sys,'platform','linux'):
     with self.assertRaises(RuntimeError):m.preflight(self.comfy,manifest)
  else:
   def test_schema_warning_explains_chroma(self):
    obj={'CreateVideo':{'input':{'required':{'chroma_subsampling':[['auto','444','422','420']]}}}};self.assertEqual(m.runtime_compatibility_warnings(obj)[0]['node'],130);self.assertEqual(m.runtime_compatibility_warnings({}),[])
 return unittest.defaultTestLoader.loadTestsFromTestCase(Tests)
if __name__=='__main__':
 for root in ROOTS:
  log=io.StringIO()
  with contextlib.redirect_stdout(log):result=unittest.TextTestRunner(stream=log,verbosity=2).run(suite(root))
  (root/'reports/installer-tests.txt').write_text(log.getvalue());(root/'reports/installer-tests.json').write_text(json.dumps({'tests':result.testsRun,'failures':len(result.failures),'errors':len(result.errors),'success':result.wasSuccessful(),'test_scope':'Temporary Linux fixtures, no Windows launcher/GPU execution'},indent=2));print(root.name,result.testsRun,result.wasSuccessful());assert result.wasSuccessful(),log.getvalue()
