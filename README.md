# hf2ollama

A tool that downloads a model from HuggingFace and converts it to GGUF for Ollama.

What it does:

1. Downloads the model from HuggingFace into `./hf/<org>/<name>/`.
2. If the repo is a **regular HF model** (has `config.json` + safetensors), clones `../llama.cpp/` (once, one level above the project) and converts it to GGUF in the same directory: `./hf/<org>/<name>/<name>.<outtype>.gguf`.
3. If the repo is a **prebuilt GGUF repo** (e.g. `*-GGUF`, containing `*.Q4_K_M.gguf` / `*.F16.gguf` and so on), conversion is skipped and one of the existing `.gguf` files is picked (priority order `Q4_K_M → Q5_K_M → Q8_0 → F16 → …`, overridable with `--quant`).
4. Writes a `Modelfile` next to the GGUF with a single line `FROM <path>.gguf`.
5. At the end prints two commands to run manually to register the model in Ollama.

## Requirements

- Python 3.11+
- `git` in `PATH` (used to clone `llama.cpp`)
- `ollama` installed (for the final commands)
- HuggingFace token with `read` scope (for private and gated models)
- Disk space: the model effectively goes onto disk twice — the source in `./hf/` and the GGUF next to it. Plan for ~25 GB for a 4B model, ~280 GB for a 70B.

## Install

```bash
git clone git@github.com:wachawo/hf2ollama.git
cd hf2ollama
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # then put your HF_TOKEN into .env
```

## Configuration

`.env` in the project root:

```ini
HF_TOKEN=hf_xxxxxxxxxxxxxxxxxxxxxxxxxxxx
# Optional. f16 (default) | f32 | bf16 | q8_0 | auto
OUTTYPE=f16
```

Get a token at <https://huggingface.co/settings/tokens> (type `Read`).

## Usage

```bash
python3 hf2ollama.py <org>/<name>
```

Optional flags:

```bash
# See which GGUF quants the repo offers (no weight download):
python3 hf2ollama.py <org>/<name>-GGUF --list

# Download a single quant — other .gguf files are skipped:
python3 hf2ollama.py <org>/<name>-GGUF --quant Q5_K_M

# Custom Ollama model name:
python3 hf2ollama.py <org>/<name> --ollama-name my-custom-name
```

The default Ollama name is derived from `<name>` (lowercased, `_` → `-`).

`--list` only hits repo metadata via `HfApi.repo_info` and prints `.gguf` filenames with sizes — nothing is written to disk.

`--quant` only matters for repos that themselves contain `.gguf` files:

- During download it sets `allow_patterns=["*<quant>*.gguf", "*.json", ...]` so only the requested quant lands on disk.
- If `--quant` is given but the repo has no `.gguf` at all, the flag is ignored and the script falls back to the normal path (HF → GGUF via `llama.cpp`).
- If `--quant` is given but matches none of the `.gguf` files in the repo, the script errors out and suggests `--list`.

For regular HF models the output GGUF format is controlled via `OUTTYPE` in `.env`.

## Examples

A public model (no token required):

```bash
python3 hf2ollama.py PantheonUnbound/Satyr-V0.1-4B
```

When it finishes the tool prints something like:

```
======================================================================
GGUF:      <repo>/hf/PantheonUnbound/Satyr-V0.1-4B/Satyr-V0.1-4B-Q4_K_M.gguf
Modelfile: <repo>/hf/PantheonUnbound/Satyr-V0.1-4B/Modelfile

Done. To import the model into Ollama, run these 2 commands:
  ollama create satyr-v0.1-4b -f <repo>/hf/PantheonUnbound/Satyr-V0.1-4B/Modelfile
  ollama run satyr-v0.1-4b
======================================================================
```

(`<repo>` is the absolute path to your clone of this repository.)

`ollama create` copies the layers into `~/.ollama/models/blobs/` and creates a manifest itself.
Do not manually copy files into `~/.ollama/models/` — Ollama stores blobs by sha256, and a manual copy will break the index.

## Project layout

```
hf2ollama/
├── .env                # HF_TOKEN, OUTTYPE
├── .gitignore
├── README.md
├── requirements.txt
├── hf2ollama.py        # the script
├── NOTES.txt           # candidate model list
│
├── hf/                 # (created by the script) HF snapshots land here
│   └── <org>/<name>/   # source + resulting GGUF + Modelfile, all in one folder
│       ├── config.json
│       ├── model.safetensors
│       ├── ...
│       ├── <name>.f16.gguf
│       └── Modelfile
└── .hf_cache/          # (created by the script) local huggingface_hub cache

../llama.cpp/           # cloned one level above the project, reusable
```

`hf/` and `.hf_cache/` are gitignored. `llama.cpp/` lives outside the project.

## Common problems

### `RepositoryNotFoundError`

The repo does not exist on HuggingFace. Some models are published elsewhere — e.g.
`xai/grok-*` is available through the xAI API rather than HF, and this pipeline cannot fetch them.

### `GatedRepoError`

The model requires accepting a license. Open the model page on HF, click "Agree and access",
and make sure the token in `.env` has access to that repo.

### `No .safetensors files found`

The repo only ships weights in legacy `pytorch_model.bin` format. By default `.bin` is excluded
to avoid duplicating safetensors. Remove `*.bin` and `*.pth` from `IGNORE_PATTERNS` in `hf2ollama.py`
and rerun.

### Out of disk / VRAM

`f16` for a 70B model is roughly 140 GB on disk and the same in VRAM when loading. Options:

- Convert to `f16` first, then quantize to `Q4_K_M` with `llama-quantize` (you'll need a built
  `llama.cpp`). `Q4_K_M` shrinks the file ~4× with minimal quality loss.
- Look for a community-built GGUF of the same model (`<org>/<name>-GGUF`) — then `hf2ollama.py`
  is unnecessary, the `.gguf` can be fed directly to `ollama create`.

## Quantization (optional, manual)

If you want `Q4_K_M` after converting to `f16`:

```bash
cd ../llama.cpp
cmake -B build && cmake --build build --target llama-quantize -j
./build/bin/llama-quantize \
    ../hf2ollama/hf/<org>/<name>/<name>.f16.gguf \
    ../hf2ollama/hf/<org>/<name>/<name>.Q4_K_M.gguf \
    Q4_K_M
```

(Run this from the `llama.cpp` clone that `hf2ollama.py` made next to this repo.)

Then update `Modelfile` (or create a new one next to it) pointing at the `Q4_K_M.gguf` and run
`ollama create` with a new name.
