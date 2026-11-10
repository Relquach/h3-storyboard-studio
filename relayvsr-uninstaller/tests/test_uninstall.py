import hashlib,importlib.util,json,pathlib,subprocess,sys,tempfile,unittest
from unittest.mock import patch
ROOT=pathlib.Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('relay_uninstall',ROOT/'scripts/uninstall.py');u=importlib.util.module_from_spec(spec);spec.loader.exec_module(u)
MODEL=u.MODELS['diffusion_models'][0];VAE=u.MODELS['vae'][0]

class RemoveTests(unittest.TestCase):
 def setUp(self):
  self.t=tempfile.TemporaryDirectory();self.base=pathlib.Path(self.t.name);self.portable=self.base/'portable';self.c=self.portable/'ComfyUI';self.c.mkdir(parents=True);self.write('main.py','core');(self.portable/'python_embeded').mkdir();(self.portable/'python_embeded/python.exe').touch();self.sdk=patch.object(u,'sdk_info',return_value={'installed':False});self.sdk.start();self.proc=patch.object(u,'active_processes',return_value=[]);self.proc.start()
 def tearDown(self):self.sdk.stop();self.proc.stop();self.t.cleanup()
 def write(self,rel,data='sentinel'):
  p=self.c/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(data);return p
 def plan(self,info=None):return u.build_plan(self.portable,info=info or {'installed':False})
 def paths(self,p):return {x['path'] for x in p['files']}
 def test_portable_root_and_child(self):
  self.assertEqual(u.portable_path(self.c),self.portable)
  with self.assertRaises(ValueError):u.portable_path(self.base)
 def test_exact_models_removed_h3_preserved(self):
  m=self.write('models/diffusion_models/'+MODEL);v=self.write('models/vae/'+VAE);h=self.write('models/diffusion_models/fasth3_omniref_8step_pruned_int8_convrot.safetensors');q=self.write('models/text_encoders/qwen.safetensors');r=u.apply_plan(self.plan());self.assertTrue(r['success']);self.assertFalse(m.exists());self.assertFalse(v.exists());self.assertEqual(h.read_text(),'sentinel');self.assertEqual(q.read_text(),'sentinel')
 def test_partial_and_corrupt_downloads_only(self):
  selected=[self.write('models/vae/'+VAE+s) for s in ['.part','.part.corrupt-123','.alias-456']];keep=self.write('models/vae/'+VAE+'.backup');bad=self.write('models/vae/'+VAE+'.part.corrupt-not-a-timestamp');u.apply_plan(self.plan());self.assertTrue(all(not x.exists() for x in selected));self.assertTrue(keep.exists() and bad.exists())
 def test_external_configured_model_path(self):
  shared=self.base/'shared';shared.mkdir();m=shared/MODEL;m.write_bytes(b'model');other=shared/'h3.safetensors';other.write_bytes(b'h3');self.write('extra_model_paths.yaml','shared:\n  base_path: '+str(self.base)+'\n  diffusion_models: shared\n');self.assertIn(str(m),self.paths(self.plan()));u.apply_plan(self.plan());self.assertFalse(m.exists());self.assertTrue(other.exists())
 def test_invalid_yaml_is_reported_not_silent_success(self):
  self.write('extra_model_paths.yaml','x: [');p=self.plan();self.assertTrue(p['scan_errors']);self.assertFalse(u.apply_plan(p)['success'])
 def test_model_subfolder_and_legacy_unet(self):
  a=self.write('models/diffusion_models/nested/'+MODEL);b=self.write('models/unet/'+MODEL);u.apply_plan(self.plan());self.assertFalse(a.exists() or b.exists())
 def test_directory_symlink_not_followed_in_model_scan(self):
  outer=self.base/'outside';outer.mkdir();f=outer/MODEL;f.write_text('keep');root=self.c/'models/diffusion_models';root.mkdir(parents=True);(root/'unregistered').symlink_to(outer,target_is_directory=True);u.apply_plan(self.plan());self.assertTrue(f.exists())
 def test_model_file_symlink_unlinks_only_link(self):
  outer=self.base/'outside';outer.write_text('keep');p=self.c/'models/vae'/VAE;p.parent.mkdir(parents=True);p.symlink_to(outer);u.apply_plan(self.plan());self.assertFalse(p.is_symlink());self.assertEqual(outer.read_text(),'keep')
 def test_node_runtime_removed_shared_nodes_preserved(self):
  dll=self.write('custom_nodes/ComfyUI-DLSS5-Enhancer/runtime/nvngx.dll');ff=self.write('custom_nodes/ComfyUI-DLSS5-Enhancer/ffmpeg/bin/ffmpeg.exe');rtx=self.write('custom_nodes/ComfyUI_Nvidia_VFX_Nodes/__init__.py');vhs=self.write('custom_nodes/ComfyUI-VideoHelperSuite/__init__.py');h3=self.write('custom_nodes/ComfyUI-H3/__init__.py');r=u.apply_plan(self.plan());self.assertTrue(r['success']);self.assertFalse(dll.exists() or ff.exists() or rtx.exists());self.assertTrue(vhs.exists() and h3.exists())
 def test_disabled_and_legacy_node_aliases(self):
  dirs=['ComfyUI-DLSS5-Enhancer-main.disabled','comfyui_nvidia_rtx_nodes','ComfyUI_Nvidia_VFX_Nodes-master']
  files=[self.write('custom_nodes/'+d+'/__init__.py') for d in dirs];u.apply_plan(self.plan());self.assertTrue(all(not p.exists() for p in files))
 def test_node_symlink_removes_link_not_external_application(self):
  outer=self.base/'app';outer.mkdir();f=outer/'nvngx.dll';f.write_text('keep');root=self.c/'custom_nodes';root.mkdir();node=root/'ComfyUI-DLSS5-Enhancer';node.symlink_to(outer,target_is_directory=True);u.apply_plan(self.plan());self.assertFalse(node.is_symlink());self.assertTrue(f.exists())
 def test_shared_backups_preserved_exclusive_backups_removed(self):
  x=self.write('user/RelayVSR_RTX_Original/backups/ComfyUI-DLSS5-Enhancer-123/runtime/nvngx.dll');y=self.write('user/RelayVSR_RTX_Original/backups/ComfyUI_Nvidia_VFX_Nodes-456/__init__.py');vhs=self.write('user/RelayVSR_RTX_Original/backups/ComfyUI-VideoHelperSuite-789/__init__.py');u.apply_plan(self.plan());self.assertFalse(x.exists() or y.exists());self.assertTrue(vhs.exists())
 def test_input_output_and_user_edited_workflow_preserved(self):
  a=self.write('input/source.mp4');b=self.write('output/vsr_upscale/video_00001.mp4');c=self.write('user/default/workflows/RelayVSR_RTX_Original/'+u.WORKFLOW,'edited');u.apply_plan(self.plan());self.assertTrue(a.exists() and b.exists() and c.exists())
 def test_original_workflow_removed_with_hash_match(self):
  f=self.write('user/default/workflows/RelayVSR_RTX_Original/'+u.WORKFLOW,'original')
  with patch.object(u,'WORKFLOW_HASH',hashlib.sha256(b'original').hexdigest()):r=u.apply_plan(self.plan())
  self.assertTrue(r['success']);self.assertFalse(f.exists())
 def test_changed_target_not_deleted(self):
  f=self.write('models/vae/'+VAE);p=self.plan();f.write_text('different file');r=u.apply_plan(p);self.assertTrue(f.exists());self.assertFalse(r['success']);self.assertTrue(r['failed'])
 def test_injected_arbitrary_saved_plan_rejected(self):
  f=self.write('models/vae/h3.safetensors');p=self.plan();p['files'].append({'path':str(f),'kind':'model','stamp':u.stat_stamp(f),'bytes':8});r=u.apply_plan(p);self.assertTrue(f.exists());self.assertFalse(r['success'])
 def test_running_comfy_blocks_deletion(self):
  f=self.write('models/vae/'+VAE);p=self.plan()
  with patch.object(u,'active_processes',return_value=[{'pid':42,'name':'python.exe'}]):
   with self.assertRaises(RuntimeError):u.apply_plan(p)
  self.assertTrue(f.exists())
 def test_deletion_failure_does_not_claim_complete(self):
  f=self.write('models/vae/'+VAE);p=self.plan()
  with patch.object(u,'remove_path',side_effect=PermissionError('locked')):r=u.apply_plan(p)
  self.assertFalse(r['success']);self.assertTrue(r['remaining_targets']);self.assertTrue(f.exists())
 def test_sdk_shared_by_other_node_kept(self):
  self.write('custom_nodes/AnotherEffect/requirements.txt','nvidia-vfx>=0.2');p=self.plan({'installed':True,'location':str(self.portable/'python_embeded/Lib/site-packages')});self.assertEqual(p['sdk']['action'],'keep')
 def test_external_sdk_kept(self):
  p=self.plan({'installed':True,'location':str(self.base/'system-python')});self.assertEqual(p['sdk']['action'],'keep')
 def test_sdk_uninstall_only_specific_distribution_and_verify_absent(self):
  info={'installed':True,'version':'0.2.0.0','location':str(self.portable/'python_embeded/Lib/site-packages')};p=self.plan(info)
  with patch.object(u.subprocess,'run',return_value=subprocess.CompletedProcess([],0,'uninstalled','')) as run,patch.object(u,'sdk_info',side_effect=[info,{'installed':False}]):r=u.apply_plan(p)
  self.assertTrue(r['success']);args=run.call_args.args[0];self.assertEqual(args[-4:],['pip','uninstall','-y','nvidia-vfx']);self.assertNotIn('torch',args);self.assertEqual(r['sdk']['action'],'uninstalled')
 def test_sdk_changed_to_external_location_not_uninstalled(self):
  info={'installed':True,'location':str(self.portable/'python_embeded/Lib/site-packages')};p=self.plan(info)
  with patch.object(u,'sdk_info',return_value={'installed':True,'location':str(self.base/'external-python')}),patch.object(u.subprocess,'run') as run:r=u.apply_plan(p)
  run.assert_not_called();self.assertEqual(r['sdk']['action'],'keep')
 def test_sdk_pip_failure_not_reported_as_success(self):
  info={'installed':True,'location':str(self.portable/'python_embeded/Lib/site-packages')};p=self.plan(info)
  with patch.object(u,'sdk_info',return_value=info),patch.object(u.subprocess,'run',return_value=subprocess.CompletedProcess([],1,'','locked')):r=u.apply_plan(p)
  self.assertFalse(r['success']);self.assertEqual(r['failed'][0]['path'],'pip:nvidia-vfx')
 def test_unknown_sdk_metadata_is_not_complete(self):
  p=self.plan({'installed':None,'error':'metadata failed'})
  with patch.object(u,'sdk_info',return_value={'installed':None,'error':'metadata failed'}):r=u.apply_plan(p)
  self.assertFalse(r['success'])
 def test_repeated_cleanup_is_idempotent(self):
  self.write('models/vae/'+VAE);self.write('custom_nodes/ComfyUI-DLSS5-Enhancer/runtime/nvngx.dll');first=u.apply_plan(self.plan());second=u.apply_plan(self.plan());self.assertTrue(first['success'] and second['success']);self.assertEqual(second['removed'],[])
 def test_no_dangerous_global_cleanup_commands(self):
  source=(ROOT/'scripts/uninstall.py').read_text();self.assertNotIn("'cache','purge'",source);self.assertNotIn('taskkill',source);self.assertNotIn('Remove-Item',source)

if __name__=='__main__':unittest.main(verbosity=2)
