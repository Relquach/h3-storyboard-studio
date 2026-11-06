"""Regression tests for Embedded Python's isolated import path."""
import json,pathlib,shutil,subprocess,sys,tempfile,unittest
ROOT=pathlib.Path(__file__).resolve().parents[1]

class PortableIsolationTests(unittest.TestCase):
    def test_entrypoints_import_with_isolated_python(self):
        for name in ['install.py','repair.py','run.py','studio.py','upgrade_workflow.py','choose_preset.py']:
            with self.subTest(name=name):
                r=subprocess.run([sys.executable,'-I',str(ROOT/'scripts'/name),'--help'],capture_output=True,text=True,cwd=tempfile.gettempdir())
                self.assertEqual(r.returncode,0,r.stderr)
                self.assertIn('usage:',r.stdout)
    def test_repair_runs_in_isolation_and_preserves_models(self):
        with tempfile.TemporaryDirectory() as d:
            root=pathlib.Path(d);package=root/'package';package.mkdir()
            shutil.copytree(ROOT/'scripts',package/'scripts',ignore=shutil.ignore_patterns('__pycache__'))
            shutil.copytree(ROOT/'custom_nodes',package/'custom_nodes',ignore=shutil.ignore_patterns('__pycache__'))
            portable=root/'portable';(portable/'python_embeded').mkdir(parents=True)
            (portable/'python_embeded/python.exe').touch()
            comfy=portable/'ComfyUI';comfy.mkdir();(comfy/'main.py').touch()
            models=comfy/'models';models.mkdir();sentinel=models/'existing-model.safetensors';sentinel.write_bytes(b'keep my model')
            args=[sys.executable,'-I',str(package/'scripts/repair.py'),'--portable',str(portable)]
            r=subprocess.run(args,capture_output=True,text=True,encoding='utf-8')
            self.assertEqual(r.returncode,0,r.stderr)
            self.assertTrue((comfy/'custom_nodes/h3_storyboard_studio/native_encoder.py').exists())
            self.assertEqual(sentinel.read_bytes(),b'keep my model')
            state=json.loads((package/'local.json').read_text())
            self.assertEqual(state['portable'],str(portable.resolve()))
            # A second repair must back up the node outside custom_nodes.
            r=subprocess.run(args,capture_output=True,text=True,encoding='utf-8')
            self.assertEqual(r.returncode,0,r.stderr)
            self.assertTrue(list((comfy/'user/h3studio_backups').iterdir()))
    def test_builder_runs_in_isolation(self):
        with tempfile.TemporaryDirectory() as d:
            r=subprocess.run([sys.executable,'-I',str(ROOT/'scripts/studio.py'),str(ROOT/'examples/project.json'),'--output',d],capture_output=True,text=True)
            self.assertEqual(r.returncode,0,r.stderr)
            g=json.loads((pathlib.Path(d)/'baseline.api.json').read_text())
            self.assertEqual(g['2']['class_type'],'H3StudioNativeClipLoader')
    def test_legacy_select_file_cannot_shadow_stdlib(self):
        with tempfile.TemporaryDirectory() as d:
            package=pathlib.Path(d)/'package'
            shutil.copytree(ROOT/'scripts',package/'scripts',ignore=shutil.ignore_patterns('__pycache__'))
            for name in ['select.py','selectors.py','socket.py']:
                (package/'scripts'/name).write_text("raise AssertionError('Package shadowed stdlib')\n")
            for isolated in [[],['-I']]:
                r=subprocess.run([sys.executable,*isolated,str(package/'scripts/install.py'),'--help'],capture_output=True,text=True)
                self.assertEqual(r.returncode,0,r.stderr)
    def test_repair_import_does_not_load_network_installer(self):
        code="import runpy,sys; runpy.run_path(sys.argv[1],run_name='repair_module'); assert 'urllib.request' not in sys.modules; assert 'install' not in sys.modules"
        r=subprocess.run([sys.executable,'-I','-c',code,str(ROOT/'scripts/repair.py')],capture_output=True,text=True)
        self.assertEqual(r.returncode,0,r.stderr)
    def test_choose_preset_import_has_no_cli_side_effects(self):
        code="import runpy,sys; runpy.run_path(sys.argv[1],run_name='choose_module')"
        r=subprocess.run([sys.executable,'-I','-c',code,str(ROOT/'scripts/choose_preset.py')],capture_output=True,text=True)
        self.assertEqual(r.returncode,0,r.stderr)
if __name__=='__main__':unittest.main()
