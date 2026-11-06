import copy
import importlib.util
import io
import json
import pathlib
import sys
import tempfile
import unittest
import zipfile
from unittest.mock import patch
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import studio
import install
spec=importlib.util.spec_from_file_location('adapter',ROOT/'custom_nodes/h3_storyboard_studio/__init__.py')
adapter=importlib.util.module_from_spec(spec);sys.modules['adapter']=adapter;spec.loader.exec_module(adapter)

class WorkflowTests(unittest.TestCase):
    def setUp(self):self.p=json.loads((ROOT/'examples/project.json').read_text())
    def test_durations_and_mapping(self):
        text,roles=studio.make_prompt(self.p)
        self.assertIn('At 00:02.000',text);self.assertIn('At 00:03.000',text)
        self.assertIn('matching <Picture 2>',text);self.assertEqual(len(roles),2)
        g=studio.build(self.p)
        self.assertEqual(g['10']['inputs']['length'],['9',0]);self.assertEqual(g['9']['inputs']['seconds'],5.0)
        self.assertEqual(g['10']['inputs']['character_1'],['6',0])
    def test_long_clip_rejected(self):
        self.p['shots'][0]['seconds']=30
        with self.assertRaises(ValueError):studio.build(self.p)
    def test_one_second_shot_retained(self):
        self.assertEqual(self.p['shots'][1]['seconds'],1.0)
        self.assertIn('Planned duration 1.0 seconds',studio.make_prompt(self.p)[0])
    def test_missing_reference_rejected(self):
        with self.assertRaises(ValueError):adapter.compose('Use <Picture 3>','["storyboard", "An"]',2)
    def test_roles_count_rejected(self):
        with self.assertRaises(ValueError):adapter.compose('','["storyboard"]',2)
    def test_enhance_preserves_audio(self):
        g=studio.build(self.p,enhance=True)
        self.assertEqual(g['20']['inputs']['audio'],g['24']['inputs']['audio'])
        self.assertEqual(g['22']['inputs']['images'],['17',0])
    def test_no_accidental_turbo_stacking(self):
        a=studio.build(self.p);b=studio.build(self.p,'turbo4')
        self.assertNotIn('11',a);self.assertEqual(b['15']['inputs']['steps'],4)
        self.assertEqual(b['12']['inputs']['model'],['11',0])
    def test_schema_mismatch_detected(self):
        with self.assertRaisesRegex(ValueError,'Missing node'):studio.check_schema(studio.build(self.p),{})
    def test_archive_traversal_blocked(self):
        with tempfile.TemporaryDirectory() as d:
            z=pathlib.Path(d)/'bad.zip'
            with zipfile.ZipFile(z,'w') as f:f.writestr('../oops','bad')
            with self.assertRaises(RuntimeError):install.safe_extract(z,pathlib.Path(d)/'out')
    def test_existing_model_never_overwritten(self):
        with tempfile.TemporaryDirectory() as d:
            p=pathlib.Path(d)/'model';p.write_bytes(b'keep')
            with self.assertRaises(RuntimeError):install.download('https://example.invalid',p,2,'0'*64)
            self.assertEqual(p.read_bytes(),b'keep')
    def test_resume_and_checksum(self):
        with tempfile.TemporaryDirectory() as d:
            p=pathlib.Path(d)/'model';p.with_name('model.part').write_bytes(b'abc')
            response=io.BytesIO(b'def');response.status=206;response.headers={'Content-Range':'bytes 3-5/6'}
            with patch('urllib.request.urlopen',return_value=response) as call:
                install.download('https://example.invalid',p,6,__import__('hashlib').sha256(b'abcdef').hexdigest())
                self.assertEqual(call.call_args[0][0].get_header('Range'),'bytes=3-')
            self.assertEqual(p.read_bytes(),b'abcdef')
    def test_bad_checksum_never_committed(self):
        with tempfile.TemporaryDirectory() as d:
            p=pathlib.Path(d)/'model';response=io.BytesIO(b'bad');response.status=200;response.headers={}
            with patch('urllib.request.urlopen',return_value=response):
                with self.assertRaisesRegex(RuntimeError,'SHA256'):install.download('https://example.invalid',p,3,'0'*64)
            self.assertFalse(p.exists())
    def test_portable_root_validation(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(ValueError):install.portable_path(d)
            p=pathlib.Path(d);(p/'python_embeded').mkdir();(p/'python_embeded/python.exe').touch();(p/'ComfyUI').mkdir();(p/'ComfyUI/main.py').touch()
            self.assertEqual(install.portable_path(d),p.resolve())
    def test_no_nan_duration(self):
        self.p['shots'][0]['seconds']=float('nan')
        with self.assertRaises(ValueError):studio.build(self.p)
    def test_duplicate_character(self):
        self.p['characters']*=2
        with self.assertRaises(ValueError):studio.build(self.p)
    def test_ui_conversion_links_roundtrip(self):
        # A minimal independent schema fixture catches link indexes/types, not a GPU integration test.
        graph={'1':{'class_type':'Source','inputs':{}},'2':{'class_type':'Sink','inputs':{'image':['1',0],'value':3}}}
        info={'Source':{'input':{'required':{}},'output':['IMAGE']},'Sink':{'input':{'required':{'image':['IMAGE'],'value':['INT',{'default':1}]}},'output':[]}}
        ui=studio.to_ui(graph,info)
        self.assertEqual(ui['links'],[[1,1,0,2,0,'IMAGE']]);self.assertEqual(ui['nodes'][1]['inputs'][0]['link'],1)
        self.assertEqual(ui['nodes'][1]['widgets_values'],[3])
    def test_reference_wrapper_forwards_original_grid(self):
        from types import ModuleType,SimpleNamespace
        module=ModuleType('comfy_extras.nodes_minimax_h3');captured={}
        class Native:
            @staticmethod
            def execute(**kw):captured.update(kw);return SimpleNamespace(result=('conditioning','latent'))
        module.MiniMaxH3ReferenceToVideo=Native
        parent=ModuleType('comfy_extras')
        with patch.dict(sys.modules,{'comfy_extras':parent,'comfy_extras.nodes_minimax_h3':module}):
            result=adapter.H3StudioReferences().encode('clip','vae','audio','whole-grid','prompt','["storyboard","An"]',640,384,124,character_1='sheet')
        self.assertEqual(captured['ref_images'],{'ref_image_0':'whole-grid','ref_image_1':'sheet'})
        self.assertEqual(result[:2],('conditioning','latent'))
    def test_reference_gap_rejected(self):
        # Import must succeed before validation; no real ComfyUI dependency needed for this check.
        from types import ModuleType
        m=ModuleType('comfy_extras.nodes_minimax_h3');m.MiniMaxH3ReferenceToVideo=object
        with patch.dict(sys.modules,{'comfy_extras':ModuleType('comfy_extras'),'comfy_extras.nodes_minimax_h3':m}):
            with self.assertRaisesRegex(ValueError,'without gaps'):
                adapter.H3StudioReferences().encode('c','v','a','grid','p','[]',640,384,124,character_2='sheet')
if __name__=='__main__':unittest.main()
