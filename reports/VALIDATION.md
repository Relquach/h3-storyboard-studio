# Validation status

Release status: experimental prototype, not GPU-qualified.

## Completed here

- 18 CPU unit tests: reference order, whole-grid forwarding, frame alignment, 1-second editorial shot, long-run rejection, model-file integrity logic, resumed download, corrupt checksum rejection, archive traversal, no existing model overwrite, graph links and schema mismatch rejection.
- Python compile check for scripts and custom nodes.
- PowerShell 7.4.6 real parser: install.ps1, start.ps1 and task.ps1 all pass syntax validation on Linux. This is not Windows execution testing.
- Network range requests reached all seven actual model URLs; reported file sizes match manifest. GGUF/safetensors/PyTorch headers have expected signatures. Model files were not downloaded in full or loaded; SHA-256 is verified during installation against provider metadata, not claimed as locally checked for all weights here.
- RealESRGAN x2plus was downloaded in full to obtain its manifest SHA-256.
- API graph structure and H3 wrapper call signature reviewed against upstream ComfyUI source and pinned H3 loader source.
- GitHub repository publishing is verified separately after upload.

## Not completed here

- No NVIDIA GPU or nvidia-smi in this environment.
- No end-to-end Windows Portable install executed.
- No H3 encoder/vision forward pass; no GGUF+Turbo runtime compatibility validation.
- No GPU sampling, video/audio decode or mux execution.
- No render of the user's 3D character, no speed/VRAM measurements, no visual quality comparison, no best-preset claim.
- UI export is only accepted after live object_info validation; a CPU fixture is not runtime certification.

The package includes local preflight, real render/benchmark logging and a human quality CSV. Run these on the target machine; provide reports and video outputs to make the next iteration evidence based. Failures must be fixed before calling this production-ready.


## v0.2.0 regression repair

Root cause reproduced from the actual Unsloth encoder header: 902 tensors, zero metadata records. The old llama.cpp GGUF text loader explicitly rejects missing general.architecture. A second mmproj was unnecessary: the native file already has 351 visual.* tensors.

All 902 native tensor names match the official Comfy-Org BF16 H3 encoder header. Exactly one shape differs: visual.patch_embed.proj.weight is stored [3456,2,16,16] instead of [1152,3,2,16,16]; loader restores the 5D view and decodes BF16 literals for vision operations. Same element count, no interpolation or new learned weights.

28 CPU regression tests pass, including format rejection, vision presence, duration conversion, graph migration and non-mutating Vietnamese layout. PowerShell scripts are syntax checked separately. These checks still do NOT constitute a successful full encoder forward pass or GPU video render. No new speed/quality claim.

Additional CPU mechanics check: gguf.GGUFReader parsed all 902 tensors from the actual header in a sparse synthetic-payload file. BF16 vision patch data was decoded and reshaped to [1152,3,2,16,16]; a real PyTorch CPU Conv3D operation produced [1,1152,1,1,1]. The payload used zeros, so this tests the repaired layout/decode mechanics only, not the original model values, full encoder or visual quality. Browser extension passed Node.js syntax validation; all four PowerShell scripts passed the real PowerShell parser.


## v0.2.1 isolated-Python regression

Reproduced the exact reported ModuleNotFoundError with `python -I scripts/repair.py --help` before patching. All six executable Python scripts now bootstrap their own trusted scripts directory before sibling imports. No global ._pth or environment changes. 31 tests pass, including actual isolated subprocess runs for CLI imports, API graph generation and repair against a temporary Portable tree. A repeated repair creates the backup outside custom_nodes and preserves a sentinel model file. No GPU/Windows-render claim is added.
