import io,unittest,pathlib,hashlib,tempfile,importlib.util
from unittest.mock import patch
ROOT=pathlib.Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location("openh3_install_dl",ROOT/"scripts/install.py");ins=importlib.util.module_from_spec(spec);spec.loader.exec_module(ins)

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
