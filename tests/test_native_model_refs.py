import importlib.util,pathlib,sys,unittest
ROOT=pathlib.Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('model_refs_nodes',ROOT/'custom_nodes/h3_storyboard_studio/__init__.py')
mod=importlib.util.module_from_spec(spec);sys.modules['model_refs_nodes']=mod;spec.loader.exec_module(mod)
from model_refs_nodes.extra_references import resolve_extras

class ExtraReferenceTests(unittest.TestCase):
    def test_bypass_never_reads_image(self):
        # No ComfyUI/nodes module is available in this test process.
        result=mod.H3StudioExtraReference().append(False,'Sword','Đạo cụ / vũ khí','(Không dùng)')[0]
        self.assertFalse(result[0]['enabled']);self.assertIsNone(result[0]['image'])
    def test_middle_bypass_remaps_in_single_pass(self):
        refs=[{'enabled':True,'image':'LAN','name':'Lan'},{'enabled':False,'image':None,'name':'Field'},
              {'enabled':True,'image':'SWORD','name':'Sword'}]
        text,active=resolve_extras('Lan <Picture 2>, field <Picture 3>, sword <Picture 4>',refs)
        self.assertTrue(text.startswith('Lan <Picture 2>, field <Picture 1>, sword <Picture 3>'))
        self.assertEqual([x['name'] for x in active],['Lan','Sword'])
    def test_all_bypassed_uses_storyboard_only(self):
        text,active=resolve_extras('Lan from <Picture 2>',[{'enabled':False,'image':None,'name':'Lan'}])
        self.assertIn('Lan from <Picture 1>',text);self.assertEqual(active,[])
    def test_annotations_do_not_need_manual_count(self):
        text=mod.compose('Lan from <Picture 2>','auto',2)
        self.assertIn('<Picture 2>',text)
        text=mod.compose('Lan from <Picture 2>','["storyboard"]',2)
        self.assertIn('<Picture 2>',text)
    def test_enabled_ref_requires_an_image(self):
        with self.assertRaisesRegex(ValueError,'chọn ảnh'):
            mod.H3StudioExtraReference().append(True,'Lan','Nhân vật','(Không dùng)')
    def test_native_model_node_registered(self):
        self.assertIn('H3StudioNativeModelLoader',mod.NODE_CLASS_MAPPINGS)
        self.assertEqual(mod.H3StudioNativeModelLoader.RETURN_TYPES,('MODEL',))

class NativeModelDirectoryTests(unittest.TestCase):
    def make_header(self,path,broken=False):
        import struct
        required={'video_patch_proj.weight':(5376,96),'audio_patch_proj.weight':(5376,32),
                  'blocks.0.attn.qkv_proj.weight':(21504,5376),'blocks.49.attn.qkv_proj.weight':(21504,5376),
                  'adaln_t_table':(1025,8)}
        if broken:required['video_patch_proj.weight']=(1,1)
        required.update({f'fixture_{i}':(1,) for i in range(500-len(required))})
        data=bytearray(b'GGUF'+struct.pack('<IQQ',3,len(required),0))
        for name,shape in required.items():
            b=name.encode();data+=struct.pack('<Q',len(b))+b+struct.pack('<I',len(shape))
            data+=struct.pack('<'+'Q'*len(shape),*reversed(shape))+struct.pack('<IQ',0,0)
        path.write_bytes(data)
    def test_native_dit_accepted_without_architecture_spoof(self):
        import tempfile
        from model_refs_nodes.native_model import inspect_native_model_header
        with tempfile.TemporaryDirectory() as d:
            p=pathlib.Path(d)/'native.gguf';self.make_header(p)
            self.assertEqual(len(inspect_native_model_header(p)),500)
    def test_wrong_dit_rejected_before_tensor_load(self):
        import tempfile
        from model_refs_nodes.native_model import inspect_native_model_header
        with tempfile.TemporaryDirectory() as d:
            p=pathlib.Path(d)/'native.gguf';self.make_header(p,broken=True)
            with self.assertRaisesRegex(ValueError,'Wrong H3 native'):inspect_native_model_header(p)
    def test_placeholder_png_crc(self):
        import tempfile,types,struct,zlib
        from unittest.mock import patch
        from model_refs_nodes.extra_references import ensure_empty_image
        with tempfile.TemporaryDirectory() as d:
            fake=types.ModuleType('folder_paths');fake.get_input_directory=lambda:d
            with patch.dict(sys.modules,{'folder_paths':fake}):name=ensure_empty_image()
            b=(pathlib.Path(d)/name).read_bytes();self.assertEqual(b[:8],b'\x89PNG\r\n\x1a\n')
            i=8
            while i<len(b):
                n=struct.unpack_from('>I',b,i)[0];tag=b[i+4:i+8];data=b[i+8:i+8+n];crc=struct.unpack_from('>I',b,i+8+n)[0]
                self.assertEqual(crc,zlib.crc32(tag+data)&0xffffffff);i+=12+n


class ReferenceIntegrationTests(unittest.TestCase):
    def test_encode_keeps_active_image_roles_after_middle_bypass(self):
        from types import ModuleType,SimpleNamespace
        from unittest.mock import patch
        captured={};native=ModuleType('comfy_extras.nodes_minimax_h3')
        class Core:
            @staticmethod
            def execute(**kw):captured.update(kw);return SimpleNamespace(result=('conditioning','latent'))
        native.MiniMaxH3ReferenceToVideo=Core
        items=[{'enabled':True,'name':'Lan','role':'Character identity','image':'LAN'},
               {'enabled':False,'name':'Rice field','role':'Environment','image':None},
               {'enabled':True,'name':'Sword','role':'Object / weapon','image':'SWORD'}]
        with patch.dict(sys.modules,{'comfy_extras':ModuleType('comfy_extras'),'comfy_extras.nodes_minimax_h3':native}):
            mod.H3StudioReferences().encode('c','v','a','GRID',
                'Lan <Picture 2>; field <Picture 3>; sword <Picture 4>', 'auto',640,384,124,extra_refs=items)
        self.assertEqual(captured['ref_images'],{'ref_image_0':'GRID','ref_image_1':'LAN','ref_image_2':'SWORD'})
        self.assertIn('<Picture 2>: Lan: Character identity',captured['prompt'])
        self.assertIn('<Picture 3>: Sword: Object / weapon',captured['prompt'])
        self.assertIn('field <Picture 1>; sword <Picture 3>',captured['prompt'])
    def test_update_installs_workflow_without_json_picker(self):
        text=(ROOT/'scripts/upgrade.ps1').read_text()
        self.assertNotIn('OpenFileDialog',text)
        self.assertIn('H3_Storyboard_VI_v0.3.json',text)
        self.assertIn('workflows\\lan-15s-vi.json',text)
    def test_bundled_ui_references_chain_and_native_model(self):
        import json
        w=json.loads((ROOT/'workflows/lan-15s-vi.json').read_text());nodes={n['id']:n for n in w['nodes']}
        self.assertEqual(nodes[1]['type'],'H3StudioNativeModelLoader')
        refs=[n for n in w['nodes'] if n['type']=='H3StudioExtraReference']
        self.assertEqual([n['widgets_values'][0] for n in refs],[True,False,False])
        self.assertEqual(nodes[9]['widgets_values'],[15.0])
        for lid,source,out,dest,slot,kind in w['links']:
            self.assertEqual(nodes[dest]['inputs'][slot]['link'],lid)
            self.assertIn(lid,nodes[source]['outputs'][out]['links'])

if __name__=='__main__':unittest.main()
