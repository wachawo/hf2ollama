# hf2ollama

[![CI](https://github.com/wachawo/hf2ollama/actions/workflows/ci.yml/badge.svg)](https://github.com/wachawo/hf2ollama/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/hf2ollama.svg)](https://pypi.org/project/hf2ollama/)
[![Downloads](https://img.shields.io/pypi/dm/hf2ollama.svg)](https://pypi.org/project/hf2ollama/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/wachawo/hf2ollama/blob/main/LICENSE)
[![Python](https://img.shields.io/pypi/pyversions/hf2ollama.svg)](https://pypi.org/project/hf2ollama/)

**[English](https://github.com/wachawo/hf2ollama/blob/main/README.md)** | [中文](https://github.com/wachawo/hf2ollama/blob/main/docs/README_ZH.md) | [हिन्दी](https://github.com/wachawo/hf2ollama/blob/main/docs/README_HI.md) | [Español](https://github.com/wachawo/hf2ollama/blob/main/docs/README_ES.md) | [Français](https://github.com/wachawo/hf2ollama/blob/main/docs/README_FR.md) | [العربية](https://github.com/wachawo/hf2ollama/blob/main/docs/README_AR.md) | [বাংলা](https://github.com/wachawo/hf2ollama/blob/main/docs/README_BN.md) | [Русский](https://github.com/wachawo/hf2ollama/blob/main/docs/README_RU.md) | [Português](https://github.com/wachawo/hf2ollama/blob/main/docs/README_PT.md) | [اردو](https://github.com/wachawo/hf2ollama/blob/main/docs/README_UR.md)

Run any HuggingFace text model inside Ollama with one command.

Point `hf2ollama` at a HuggingFace repo — it fetches the model, converts it
to the GGUF format Ollama needs, and prints the two `ollama` commands you
run to register and chat with it. No manual `convert_hf_to_gguf.py`,
no hand-written `Modelfile`.

Requires Python 3.11+ and a working [Ollama](https://ollama.com) install.

---

## Install

```bash
pip install hf2ollama
```

---

## Usage

Put your HuggingFace token in a `.env` next to where you'll run the command,
then point the tool at a repo:

```bash
echo "HF_TOKEN=hf_xxxxxxxxxxxxxxxxxxxxxxxxxxxx" > .env
hf2ollama SicariusSicariiStuff/Assistant_Pepe_70B
```

When it finishes, the tool prints two commands. Run them and you're chatting:

```
ollama create assistant-pepe-70b -f <path>/Modelfile
ollama run assistant-pepe-70b
```

(Get a HuggingFace token at <https://huggingface.co/settings/tokens> with `Read` scope.
It's needed only for private and gated models, but having one set never hurts.)

### Optional flags

```bash
# See which GGUF quants are inside a *-GGUF repo (no download):
hf2ollama some-user/some-model-GGUF --list

# Download a single quant — other .gguf files are skipped:
hf2ollama some-user/some-model-GGUF --quant Q5_K_M

# Custom Ollama model name:
hf2ollama some-user/some-model --ollama-name my-model
```

---

## Install from git

For the latest unreleased changes:

```bash
pip install git+https://github.com/wachawo/hf2ollama.git
# or, over SSH:
pip install git+ssh://git@github.com/wachawo/hf2ollama.git
```

## Install from source

For local development:

```bash
git clone git@github.com:wachawo/hf2ollama.git
cd hf2ollama
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
cp .env.example .env   # then put your HF_TOKEN into .env
hf2ollama --help
```

---

## Configuration

`.env` in the directory you run `hf2ollama` from:

```ini
HF_TOKEN=hf_xxxxxxxxxxxxxxxxxxxxxxxxxxxx
# Optional. f16 (default) | f32 | bf16 | q8_0 | auto
OUTTYPE=f16
```

### Path overrides

Everything is written under the current working directory. Override with env vars
if you want to share things between workspaces:

| Variable                     | Default                       | Purpose                                |
|------------------------------|-------------------------------|----------------------------------------|
| `HF2OLLAMA_WORKSPACE`        | `$PWD`                        | Base directory for everything below.   |
| `HF2OLLAMA_HF_DIR`           | `<workspace>/hf`              | Where HF snapshots and GGUFs go.       |
| `HF2OLLAMA_CACHE_DIR`        | `<workspace>/.hf_cache`       | `huggingface_hub` cache.               |
| `HF2OLLAMA_LLAMA_CPP_DIR`    | `<workspace>/../llama.cpp`    | Where to clone `llama.cpp`.            |

---

## What ends up on disk

```
<workspace>/
├── .env                # HF_TOKEN, OUTTYPE
├── hf/                 # HF snapshots land here
│   └── <org>/<name>/   # source files + resulting GGUF + Modelfile, all in one folder
│       ├── config.json
│       ├── model.safetensors
│       ├── ...
│       ├── <name>.f16.gguf
│       └── Modelfile
└── .hf_cache/          # local huggingface_hub cache

<workspace>/../llama.cpp/   # cloned once, reused across workspaces
```

The first run also clones [`llama.cpp`](https://github.com/ggerganov/llama.cpp)
one level above your workspace so the next run is fast. Only repos that ship
prebuilt GGUF files skip this step.

## Example output

```
======================================================================
GGUF:      <workspace>/hf/SicariusSicariiStuff/Assistant_Pepe_70B/Assistant_Pepe_70B.f16.gguf
Modelfile: <workspace>/hf/SicariusSicariiStuff/Assistant_Pepe_70B/Modelfile

Done. To import the model into Ollama, run these 2 commands:
  ollama create assistant-pepe-70b -f <workspace>/hf/SicariusSicariiStuff/Assistant_Pepe_70B/Modelfile
  ollama run assistant-pepe-70b
======================================================================
```

`ollama create` copies the layers into `~/.ollama/models/blobs/` and creates
a manifest itself. Do **not** manually copy files into `~/.ollama/models/` —
Ollama stores blobs by sha256, and a manual copy will break its index.

---

## Troubleshooting

### `RepositoryNotFoundError`

The repo does not exist on HuggingFace. Some models are published elsewhere —
e.g. `xai/grok-*` lives behind the xAI API rather than HF, and this pipeline
cannot fetch it.

### `GatedRepoError`

The model requires accepting a license. Open the model page on HF, click
"Agree and access", and make sure the token in `.env` has access to that repo.

### `No .safetensors files found`

The repo only ships weights in the legacy `pytorch_model.bin` format. By default
`.bin` is excluded to avoid duplicating safetensors. Remove `*.bin` and `*.pth`
from `IGNORE_PATTERNS` in `hf2ollama.py` and rerun.

### Out of disk or VRAM

`f16` for a 70B model is roughly 140 GB on disk and the same in VRAM when
loading. Two ways out:

- Convert to `f16` first, then quantize to `Q4_K_M` (see below) — `Q4_K_M`
  shrinks the file ~4× with minimal quality loss.
- Look for a community-built GGUF of the same model (`<org>/<name>-GGUF`) —
  then `--list` will show available quants, and `--quant Q4_K_M` downloads
  just the one you want.

---

## Manual quantization (optional)

If you've converted to `f16` and want a smaller `Q4_K_M`:

```bash
cd ../llama.cpp
cmake -B build && cmake --build build --target llama-quantize -j
./build/bin/llama-quantize \
    <workspace>/hf/<org>/<name>/<name>.f16.gguf \
    <workspace>/hf/<org>/<name>/<name>.Q4_K_M.gguf \
    Q4_K_M
```

Then create a new `Modelfile` pointing at the `Q4_K_M.gguf` and run
`ollama create` with a new name.
