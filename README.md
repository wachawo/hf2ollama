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

### Option A — pip install from git (recommended)

```bash
pip install git+https://github.com/wachawo/hf2ollama.git
# or, over SSH:
pip install git+ssh://git@github.com/wachawo/hf2ollama.git
```

This installs the `hf2ollama` command into your active environment.
Then create a `.env` (or export `HF_TOKEN=...`) in the directory you'll run from:

```bash
mkdir -p ~/llm-workspace && cd ~/llm-workspace
cat > .env <<EOF
HF_TOKEN=hf_xxxxxxxxxxxxxxxxxxxxxxxxxxxx
OUTTYPE=f16
EOF
hf2ollama SicariusSicariiStuff/Assistant_Pepe_70B
```

Models land in `./hf/<org>/<name>/`, the HF cache in `./.hf_cache/`, and `llama.cpp`
is cloned to `../llama.cpp/` (one level above the workspace, so it can be reused
across several workspaces).

### Option B — clone and run from a checkout

```bash
git clone git@github.com:wachawo/hf2ollama.git
cd hf2ollama
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # then put your HF_TOKEN into .env
python3 hf2ollama.py SicariusSicariiStuff/Assistant_Pepe_70B
```

### Path overrides

All paths default to the current working directory but can be overridden with env vars:

| Variable                     | Default                       | Purpose                                |
|------------------------------|-------------------------------|----------------------------------------|
| `HF2OLLAMA_WORKSPACE`        | `$PWD`                        | Base directory for everything below.   |
| `HF2OLLAMA_HF_DIR`           | `<workspace>/hf`              | Where HF snapshots and GGUFs go.       |
| `HF2OLLAMA_CACHE_DIR`        | `<workspace>/.hf_cache`       | `huggingface_hub` cache.               |
| `HF2OLLAMA_LLAMA_CPP_DIR`    | `<workspace>/../llama.cpp`    | Where to clone `llama.cpp`.            |

## Configuration

`.env` in the project root:

```ini
HF_TOKEN=hf_xxxxxxxxxxxxxxxxxxxxxxxxxxxx
# Optional. f16 (default) | f32 | bf16 | q8_0 | auto
OUTTYPE=f16
```

Get a token at <https://huggingface.co/settings/tokens> (type `Read`).

## Usage

After `pip install`, the command is just `hf2ollama`. From a checkout, use `python3 hf2ollama.py`. Both forms are equivalent below.

```bash
hf2ollama <org>/<name>
```

Optional flags:

```bash
# See which GGUF quants the repo offers (no weight download):
hf2ollama <org>/<name>-GGUF --list

# Download a single quant — other .gguf files are skipped:
hf2ollama <org>/<name>-GGUF --quant Q5_K_M

# Custom Ollama model name:
hf2ollama <org>/<name> --ollama-name my-custom-name
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
hf2ollama SicariusSicariiStuff/Assistant_Pepe_70B
```

When it finishes the tool prints something like:

```
======================================================================
GGUF:      <repo>/hf/SicariusSicariiStuff/Assistant_Pepe_70B/Assistant_Pepe_70B.f16.gguf
Modelfile: <repo>/hf/SicariusSicariiStuff/Assistant_Pepe_70B/Modelfile

Done. To import the model into Ollama, run these 2 commands:
  ollama create assistant-pepe-70b -f <repo>/hf/SicariusSicariiStuff/Assistant_Pepe_70B/Modelfile
  ollama run assistant-pepe-70b
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

## Releases

Releases are cut by pushing a git tag. The `Publish` workflow
(`.github/workflows/publish.yml`) reacts to tags matching `*.*.*` or `v*`, builds
sdist + wheel with `python -m build`, and uploads them to PyPI via PyPA's
trusted publishing action (`pypa/gh-action-pypi-publish`).

To release a new version:

```bash
# 1. Bump the version in pyproject.toml (e.g. 0.1.0 -> 0.1.1)
# 2. Commit, tag, push
git commit -am "release 0.1.1"
git tag 0.1.1
git push origin main --tags
```

The tag push triggers `.github/workflows/publish.yml` and, if the project is
configured as a Trusted Publisher on PyPI, the new version appears on
<https://pypi.org/project/hf2ollama/> a minute later.

### One-time PyPI setup

PyPI Trusted Publishing replaces the old `PYPI_API_TOKEN` secret with a
GitHub Actions OIDC handshake. Configure it once:

1. <https://pypi.org/manage/account/publishing/> → "Add a new pending publisher".
2. Project name: `hf2ollama`. Owner: `wachawo`. Repository: `hf2ollama`.
   Workflow: `publish.yml`. Environment: leave empty.
3. After the first successful release, the publisher becomes permanent.

No API tokens are stored in GitHub Secrets — the workflow uses `permissions: id-token: write`.

## Continuous integration

`.github/workflows/ci.yml` runs on every push and PR to `main`/`master`:

- installs the package with `pip install -e .` on Linux + macOS, Python 3.11 / 3.12 / 3.13
- runs `hf2ollama --help` and a malformed-argument smoke test
- builds sdist and wheel with `python -m build` and uploads them as a build
  artifact (useful for testing the package before tagging)

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
