import copy,importlib.util,json,pathlib,struct,sys,tempfile,unittest
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from upgrade_workflow import migrate_ui
from workflow_ui import beautify
import studio
spec=importlib.util.spec_from_file_location('h3_nodes_v2',ROOT/'custom_nodes/h3_storyboard_studio/__init__.py')
mod=importlib.util.module_from_spec(spec);sys.modules['h3_nodes_v2']=mod;spec.loader.exec_module(mod)
native=sys.modules['h3_nodes_v2.native_encoder']


def native_header(path,missing=None,wrong_shape=False,metadata=0):
    entries={
      'model.embed_tokens.weight':(151936,5120),
      'model.layers.0.self_attn.q_proj.weight':(8192,5120),
      'model.layers.49.self_attn.q_proj.weight':(8192,5120),
      'visual.patch_embed.proj.weight':(3456,2,16,16),
      'visual.pos_embed.weight':(2304,1152),
      'visual.blocks.0.attn.qkv.weight':(3456,1152),
      'visual.merger.linear_fc1.weight':(4608,4608),
      'visual.deepstack_merger_list.0.linear_fc1.weight':(4608,4608)}
    if missing:del entries[missing]
    if wrong_shape:entries['model.embed_tokens.weight']=(10,10)
    entries.update({f'test_unused_{i}':(1,) for i in range(500-len(entries))})
    data=bytearray(b'GGUF'+struct.pack('<IQQ',3,len(entries),metadata))
    for name,shape in entries.items():
        b=name.encode();data+=struct.pack('<Q',len(b))+b+struct.pack('<I',len(shape))
        data+=struct.pack('<'+'Q'*len(shape),*reversed(shape))+struct.pack('<IQ',30,0)
    path.write_bytes(data)


class UpgradeTests(unittest.TestCase):
    def test_native_header_with_embedded_vision(self):
        with tempfile.TemporaryDirectory() as d:
            p=pathlib.Path(d)/'native.gguf';native_header(p)
            tensors=native.inspect_native_header(p)
            self.assertEqual(len(tensors),500)
            self.assertIn('visual.pos_embed.weight',tensors)
    def test_missing_vision_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            p=pathlib.Path(d)/'native.gguf';native_header(p,missing='visual.pos_embed.weight')
            with self.assertRaisesRegex(ValueError,'vision tower'):native.inspect_native_header(p)
    def test_llama_format_not_silently_reinterpreted(self):
        with tempfile.TemporaryDirectory() as d:
            p=pathlib.Path(d)/'native.gguf';native_header(p,metadata=1)
            with self.assertRaisesRegex(ValueError,'metadata-free'):native.inspect_native_header(p)
    def test_wrong_model_dimensions_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            p=pathlib.Path(d)/'native.gguf';native_header(p,wrong_shape=True)
            with self.assertRaisesRegex(ValueError,'expected native'):native.inspect_native_header(p)
    def test_visible_duration_control(self):
        self.assertEqual(mod.H3StudioDuration().calculate(15),(362,362/24))
        self.assertEqual(mod.H3StudioDuration().calculate(5),(124,124/24))
        with self.assertRaises(ValueError):mod.duration_to_frames(30)
    def test_new_graph_uses_native_loader_and_seconds(self):
        p=json.loads((ROOT/'examples/project.json').read_text());g=studio.build(p)
        self.assertEqual(g['2']['class_type'],'H3StudioNativeClipLoader')
        self.assertNotIn('mmproj_name',g['2']['inputs'])
        self.assertEqual(g['10']['inputs']['length'],['9',0])
    def old_ui(self):
        return {'nodes':[
          {'id':2,'type':'H3ClipLoaderAny','widgets_values':[studio.MODELS['clip'],'minimax','old-mmproj'],
           'inputs':[],'outputs':[{'name':'CLIP','type':'CLIP','links':[1]}],'properties':{}},
          {'id':5,'type':'LoadImage','widgets_values':['my-actual-storyboard.png','image'],'inputs':[],
           'outputs':[{'name':'IMAGE','type':'IMAGE','links':[]}],'properties':{}},
          {'id':10,'type':'H3StudioReferences','widgets_values':['MY EXACT PROMPT','["storyboard"]',576,1024,362,'max'],
           'inputs':[{'name':'clip','type':'CLIP','link':1}],'outputs':[],'properties':{}}],
          'links':[[1,2,0,10,0,'CLIP']],'last_node_id':10,'last_link_id':1,'version':0.4}
    def test_migration_preserves_user_prompt_images_and_links(self):
        old=self.old_ui();before=copy.deepcopy(old);w=migrate_ui(old)
        self.assertEqual(old,before)
        nodes={n['id']:n for n in w['nodes']}
        self.assertEqual(nodes[2]['type'],'H3StudioNativeClipLoader')
        self.assertEqual(nodes[5]['widgets_values'][0],'my-actual-storyboard.png')
        self.assertEqual(nodes[10]['widgets_values'],old['nodes'][2]['widgets_values'])
        self.assertIn(old['links'][0],w['links'])
        timer=next(n for n in w['nodes'] if n['type']=='H3StudioDuration')
        self.assertEqual(timer['widgets_values'],[15.0])
        self.assertEqual(timer['title'],'03 · THỜI LƯỢNG CLIP (GIÂY)')
    def test_migration_idempotent(self):
        first=migrate_ui(self.old_ui());second=migrate_ui(first)
        self.assertEqual(sum(n['type']=='H3StudioDuration' for n in second['nodes']),1)
        self.assertEqual(len(second['links']),len(first['links']))
    def test_style_does_not_rewire_execution(self):
        old=self.old_ui();w=beautify(old)
        self.assertEqual(w['links'],old['links'])
        self.assertEqual(w['nodes'][2]['widgets_values'],old['nodes'][2]['widgets_values'])
        self.assertEqual(len(w['groups']),5)
    def test_manifest_no_extra_vision_download(self):
        manifest=json.loads((ROOT/'manifest.json').read_text())
        self.assertFalse(any('mmproj' in x['file'] for x in manifest['models']))
if __name__=='__main__':unittest.main()
