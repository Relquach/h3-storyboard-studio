// Freezes the audio in the UNTILED branch of MMH3 Ultimate Upscale, the same way
// its tiled branches already do. Without it, pass 2 re-noises and regenerates the
// audio, the video lip-syncs to that new audio, and the node then throws it away
// and keeps the pass 1 audio - so mouths move to speech you never hear.
//
// Run:   node patch_h3_upscale_audio_freeze.js
// Undo:  copy nodes.py.orig-before-audio-freeze back over nodes.py
// Safe to run twice: it does nothing if the patch is already in.

const fs = require('fs');
const path = require('path');

const file = process.argv[2] || path.join(process.env.LOCALAPPDATA,
  'Comfy-Desktop', 'ComfyUI-Installs', 'ANKIT', 'ComfyUI', 'custom_nodes',
  'plaguekind-nodes', 'ComfyUI-H3-UltimateUpscale-LD', 'nodes.py');

const src = fs.readFileSync(file, 'utf8');
const MARK = '# h3-audio-freeze patch';
if (src.includes(MARK)) {
  console.log('Already patched:', file);
  process.exit(0);
}

const eol = src.includes('\r\n') ? '\r\n' : '\n';
const old = '                piece = {"samples": comfy.nested_tensor.NestedTensor((chunk_v, chunk_a))}' + eol +
            '                out = sample_piece(piece, cond_i, model, noise, sampler, sigmas, negative, cfg)';
const hits = src.split(old).length - 1;
if (hits !== 1) {
  console.error('Expected the untiled sample block exactly once, found ' + hits + '. Not patching.');
  process.exit(1);
}

const neu = [
  '                ' + MARK + ': freeze the audio (mask 0) like the tiled paths do,',
  '                # so the video lip-syncs to the pass 1 audio that is kept below',
  '                mv = torch.ones((1, 1, 1, chunk_v.shape[3], chunk_v.shape[4]),',
  '                                device=chunk_v.device, dtype=torch.float32)',
  '                ma = torch.zeros((1, 32, 2, chunk_a.shape[-1]),',
  '                                 device=chunk_a.device, dtype=chunk_a.dtype)',
  '                piece = {',
  '                    "samples": comfy.nested_tensor.NestedTensor((chunk_v, chunk_a)),',
  '                    "noise_mask": comfy.nested_tensor.NestedTensor((mv, ma)),',
  '                }',
  '                out = sample_piece(piece, cond_i, model, noise, sampler, sigmas, negative, cfg)',
].join(eol);

const backup = file + '.orig-before-audio-freeze';
if (!fs.existsSync(backup)) fs.copyFileSync(file, backup);
fs.writeFileSync(file, src.replace(old, neu));
console.log('Patched:', file);
console.log('Backup: ', backup);
console.log('Restart ComfyUI so the change loads.');
