# Repository instructions for AI coding agents

These guidelines apply when an AI coding assistant (Claude Code, OpenAI
Codex, Cursor, or similar) works on this repository. `CLAUDE.md` and
`AGENTS.md` are kept byte-identical by a pre-commit hook — edit
`CLAUDE.md` and the hook copies it onto `AGENTS.md` before the commit
is finalised. Treat `CLAUDE.md` as the canonical source.

## What this project is

A single-module Python CLI (`hf2ollama.py`) that downloads a HuggingFace
text model, converts it to GGUF via `llama.cpp`, writes an Ollama
`Modelfile`, and prints the two `ollama` commands the user runs to register
the model. Distributed on PyPI as `hf2ollama`; entry point
`hf2ollama = "hf2ollama:main"` in `pyproject.toml`.

## Common commands

```bash
# Dev install (in an activated venv)
pip install -e ".[dev]"
pre-commit install

# Run the tool against a HF repo (writes into the current working directory)
hf2ollama <org>/<name>
hf2ollama <org>/<name>-GGUF --list
hf2ollama <org>/<name>-GGUF --quant Q4_K_M

# Code quality (all three are wired into pre-commit too)
black .
ruff check . --fix
mypy hf2ollama.py

# Run every pre-commit hook on the whole repo (mirrors what CI does)
pre-commit run --all-files

# Build sdist + wheel (CI does this on every push; publish.yml does it on tag)
python -m build
```

There is no test suite. CI exercises `hf2ollama --help` and an argv
validation check; do not invent a `pytest` config.

## Architecture and important invariants

### Workspace is the **current working directory**, not the script's location

`BASE_DIR = Path(os.getenv("HF2OLLAMA_WORKSPACE", str(Path.cwd()))).resolve()`

This is deliberate. After `pip install hf2ollama`, the entry point lives in
`site-packages/`; if `BASE_DIR` were derived from `__file__`, models would
land inside the venv. Do **not** revert to `Path(__file__).parent`. All
other paths (`HF_DIR`, `HF_CACHE_DIR`, `LLAMA_CPP`) hang off `BASE_DIR` and
each has its own `HF2OLLAMA_*` override.

### Everything stays inside the workspace

`os.environ.setdefault("HF_HOME", str(HF_CACHE_DIR))` and
`HF_HUB_CACHE` are set at import time so `huggingface_hub` never writes
to `~/.cache/huggingface/`. `cache_dir=` is also passed explicitly to
`snapshot_download`. Keep both.

### `llama.cpp` lives one directory above the workspace by default

`LLAMA_CPP = BASE_DIR.parent / "llama.cpp"`. The intent is to share the
clone across several workspace directories. The clone is created lazily
inside `ensure_llama_cpp()` and only when conversion is actually required.

### Three execution paths in `main()`

After the repo snapshot is downloaded into `HF_DIR/<org>/<name>/`, the
decision tree is:

1. **Repo ships `.gguf` files** → `find_existing_ggufs()` returns them,
   `pick_gguf(preferred=args.quant)` selects one using `QUANT_PRIORITY`,
   conversion is **skipped** (no `llama.cpp` clone needed).
2. **Repo has `config.json`** (normal HF transformers model) → clone
   `llama.cpp`, install its conversion requirements, and run
   `convert_hf_to_gguf.py`.
3. **Neither** → exit with an explanatory error. Often gated repo or an
   adapter-only repository.

`--list` short-circuits before download and only hits
`HfApi.repo_info(model_id, files_metadata=True)`.

`--quant Q*` is validated **before** download against the same `repo_info`
result, then converted into `allow_patterns=["*Q*.gguf", *QUANT_ALLOW_PATTERNS]`
so unwanted quants never hit disk.

### Output file layout

```
<workspace>/hf/<org>/<name>/
├── config.json, model.safetensors, ...   (HF source files)
├── <name>.f16.gguf                       (or repo-shipped GGUF, untouched)
└── Modelfile                             (single line: `FROM <gguf_path>`)
```

`Modelfile` is always named `Modelfile` (Ollama convention). `write_modelfile()`
takes only `gguf_path` — model_id is not needed for the file contents.

## Tooling configuration

All linter/formatter/type-checker configs live in `pyproject.toml`:

- `[tool.black]` — line length 180, target py311
- `[tool.ruff]` — line length 180, rule set `E,W,F,I,B,C4,UP,SIM`,
  ignores `E501` (long lines, capped already by line-length) and `UP009`
  (the `# -*- coding: utf-8 -*-` header is kept on purpose)
- `[tool.mypy]` — py311, `warn_return_any`, `warn_unused_ignores`,
  `ignore_missing_imports`

`huggingface_hub`'s `repo_info` returns a `ModelInfo | DatasetInfo | SpaceInfo | KernelInfo`
union; `KernelInfo` has no `siblings` attribute. Access via
`getattr(info, "siblings", None) or []` rather than `info.siblings`.

`snapshot_download` kwargs are heterogeneous (`str | None` plus
`list[str]`). Build the dict as `dict[str, Any]` to keep mypy happy.

## GitHub workflows

- `.github/workflows/ci.yml` — install matrix (Linux + macOS, Python
  3.11/3.12/3.13), `hf2ollama --help` smoke, build artifact upload.
- `.github/workflows/publish.yml` — triggers on tag pushes matching
  `*.*.*` or `v*`, builds and uploads to PyPI using
  `pypa/gh-action-pypi-publish` via **trusted publishing**. No PyPI
  API token is or should be added to GitHub Secrets.
- `.github/workflows/check-issue.yml` — uses `pull_request_target` so
  forks can be checked safely. Fails the check unless the PR title/body
  contains `Fixes #N` / `Closes #N` / `Resolves #N` **and** the author is
  in that issue's `assignees`. Bots are exempt. To make this actually
  block merges, the workflow must be added to required status checks in
  branch protection on `main`.

Release flow: bump `version` in `pyproject.toml`, commit, tag (`0.1.0`
or `v0.1.0`), `git push --tags`. `publish.yml` does the rest.

## Translations

`docs/README_*.md` contains nine localized copies of the README
(ZH, HI, ES, FR, AR, BN, RU, PT, UR). They all share the same structure
and a 10-language switcher on line 9. When changing the English
`README.md`:

- update the same section in each locale, or note that it's pending,
- preserve the language switcher order: English → 中文 → हिन्दी →
  Español → Français → العربية → বাংলা → Русский → Português → اردو,
- bold the active language in each file.

Code blocks, file paths, environment variable names, and CLI flags stay
in English in every locale.

## Pull request policy (read before opening a PR)

`.github/workflows/check-issue.yml` is an automatic gatekeeper. PRs that do
not satisfy **all** of the following will be marked failing and, once the
check is required in branch protection, blocked from merging:

1. The PR title or body contains a GitHub linking keyword pointing at an
   issue in this repository: `Fixes #N` / `Closes #N` / `Resolves #N`
   (any case, common inflections accepted).
2. That issue exists and is open in `wachawo/hf2ollama` — cross-repo
   references and PR-number references do not count.
3. The PR author is listed in the issue's `assignees`. A maintainer must
   assign the issue first; self-assignment by a non-collaborator is not
   possible on GitHub.

Bots (dependabot, renovate, github-actions[bot]) are exempted by the
workflow's `if:` guard.

### What the AI assistant must do before drafting a PR

Before running `gh pr create`, or before suggesting it to the user, the
AI assistant must explicitly confirm:

- **There is an issue.** If the user hasn't filed one yet, stop and tell
  them to create the issue first and have a maintainer assign it. Do not
  paper over this by opening the PR anyway — the check will fail and the
  user wastes a round trip.
- **The user is the assignee.** Ask if you don't know. Suggest
  `gh issue view <N> --json assignees` to verify.
- **The PR body contains the linking keyword.** Put `Fixes #N` (preferred)
  or one of the alternatives in the body, not just the title — both are
  scanned, but body is the convention.

### Disclosure when AI assistance is used

If an AI assistant materially helped draft a change, mention it briefly
in both the commit message and the PR description — one short sentence
naming the agent that was used (e.g. _Drafted with the help of Claude
Code._ or _Authored with assistance from OpenAI Codex._). No specific
template, no machine-readable tag, no `Co-Authored-By:` trailer — just
a free-form acknowledgement so a reviewer knows where the change came
from.

Apply this whenever AI assistance went beyond minor tab-completion:
writing new functions, refactoring more than a few lines, generating
tests, authoring the PR description itself, or composing the commit
message. When in doubt, include it.

## Style conventions specific to this repo

- Single module — do not split `hf2ollama.py` into a package without
  also updating `[tool.setuptools] py-modules` and the entry point.
- No leading underscores on function or variable names. Use
  `sibling_size`, not `_sibling_size`.
- Keep the `LOGGING: dict[str, Any] = {...}; logging.basicConfig(**LOGGING)`
  pattern; the explicit `Any` is required for mypy.
- The final user-facing summary block in `main()` deliberately calls
  `sys.stderr.flush()` + `sys.stdout.flush()` and uses `print(..., flush=True)`
  so the trailing tqdm "Download complete:" line from `huggingface_hub`
  cannot land after our banner.
