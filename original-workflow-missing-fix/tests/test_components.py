import pathlib,sys,tempfile,unittest,shutil
from unittest.mock import patch
ROOT=pathlib.Path(__file__).resolve().parents[1];sys.path.append(str(ROOT/'scripts'))
import components
class ComponentTests(unittest.TestCase):
 def source(self,root):
  p=pathlib.Path(root)/'source';p.mkdir();(p/'__init__.py').write_text('# source');return p
 def test_bundled_sources_present(self):
  for name in ['comfyui-h3-take','comfyui-video-finishing']:self.assertTrue((ROOT/'bundled-nodes'/name/'__init__.py').is_file())
 def test_nested_plague_reused_instead_of_duplicate_pack(self):
  with tempfile.TemporaryDirectory() as d:
   p=pathlib.Path(d)/'custom_nodes/PlagueKind/ComfyUI-H3-UltimateUpscale-LD';p.mkdir(parents=True);(p/'__init__.py').touch()
   self.assertEqual(components.find_target(d,'ComfyUI-H3-UltimateUpscale-LD'),p)
 def test_duplicate_pack_detected(self):
  with tempfile.TemporaryDirectory() as d:
   for folder in ['custom_nodes/PlagueKind/ComfyUI-H3-UpscaleSize','custom_nodes/ComfyUI-H3-UpscaleSize']:
    p=pathlib.Path(d)/folder;p.mkdir(parents=True);(p/'__init__.py').touch()
   with self.assertRaises(ValueError):components.find_target(d,'ComfyUI-H3-UpscaleSize')
 def test_idempotence_and_backup_outside_custom(self):
  with tempfile.TemporaryDirectory() as d:
   root=pathlib.Path(d);source=self.source(root);comfy=root/'ComfyUI';target=comfy/'custom_nodes/comfyui-h3-take';target.mkdir(parents=True);(target/'__init__.py').write_text('# old')
   components.put_component(comfy,'comfyui-h3-take',source);components.put_component(comfy,'comfyui-h3-take',source)
   backups=list((comfy/'user/h3_missing_fix/backups').iterdir());self.assertEqual(len(backups),1);self.assertEqual((backups[0]/'__init__.py').read_text(),'# old')
 def test_failed_copy_restores_old(self):
  with tempfile.TemporaryDirectory() as d:
   root=pathlib.Path(d);source=self.source(root);comfy=root/'ComfyUI';target=comfy/'custom_nodes/comfyui-h3-take';target.mkdir(parents=True);(target/'__init__.py').write_text('# keep')
   with patch.object(components.shutil,'copytree',side_effect=OSError('fixture')):
    with self.assertRaises(OSError):components.put_component(comfy,'comfyui-h3-take',source)
   self.assertEqual((target/'__init__.py').read_text(),'# keep')
 def test_audio_freeze_and_idempotence(self):
  with tempfile.TemporaryDirectory() as d:
   p=pathlib.Path(d)/'nodes.py';p.write_bytes(b'def fixture():\r\n                piece = {"samples": comfy.nested_tensor.NestedTensor((chunk_v, chunk_a))}\r\n                out = sample_piece(piece, cond_i, model, noise, sampler, sigmas, negative, cfg)\r\n')
   self.assertTrue(components.freeze_audio(p));self.assertFalse(components.freeze_audio(p));compile(p.read_text(),str(p),'exec');self.assertIn('noise_mask',p.read_text());self.assertTrue(p.with_suffix('.py.before-audio-freeze').exists())
 def test_audio_freeze_refuses_unknown_source(self):
  with tempfile.TemporaryDirectory() as d:
   p=pathlib.Path(d)/'nodes.py';p.write_text('# unrelated')
   with self.assertRaises(ValueError):components.freeze_audio(p)
   self.assertEqual(p.read_text(),'# unrelated')
if __name__=='__main__':unittest.main()
