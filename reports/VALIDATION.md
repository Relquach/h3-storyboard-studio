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
