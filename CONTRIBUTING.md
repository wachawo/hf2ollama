# Contributing

Thanks for considering a contribution to `hf2ollama`. This file covers the
local development setup, code quality tools, and the release process.

## Development setup

```bash
git clone git@github.com:wachawo/hf2ollama.git
cd hf2ollama

# Create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install the package in editable mode together with dev tools
# (pre-commit, black, ruff, mypy, build)
pip install -e ".[dev]"

# Install the git hook so checks run on every commit
pre-commit install

# Optional: run all hooks once over the whole repo
pre-commit run --all-files
```

## Code quality

The project enforces three tools, configured in `pyproject.toml` and wired
into pre-commit via `.pre-commit-config.yaml`:

| Tool   | Role                            | Config in `pyproject.toml` |
|--------|---------------------------------|----------------------------|
| black  | Formatter (line length = 180)   | `[tool.black]`             |
| ruff   | Linter (E, W, F, I, B, C4, UP, SIM) | `[tool.ruff]`          |
| mypy   | Static type checker             | `[tool.mypy]`              |

Run individually:

```bash
black .
ruff check . --fix
mypy hf2ollama.py
```

Or all at once through pre-commit (recommended — same versions as CI):

```bash
pre-commit run --all-files                # everything
pre-commit run black --all-files          # one hook
pre-commit run ruff --all-files
pre-commit run mypy --all-files
pre-commit autoupdate                     # bump hook revisions in .pre-commit-config.yaml
```

### When pre-commit blocks a commit

If `black` or `ruff` reformat files, the commit is aborted with the changes
applied to your working tree. Stage them and commit again:

```bash
git add -u
git commit
```

Do **not** bypass hooks with `git commit --no-verify` unless you understand
why the hook is failing.

## Continuous integration

`.github/workflows/ci.yml` runs on every push and PR to `main`/`master`:

- Installs the package on Linux and macOS with Python 3.11 / 3.12 / 3.13
- Runs `hf2ollama --help` and an argv-validation smoke test
- Builds `sdist` + `wheel` with `python -m build` and uploads them as an
  artifact

`.github/workflows/check-issue.yml` runs on every PR event. It blocks the PR
unless the description references an open issue (`Fixes #123`,
`Closes #123`, `Resolves #123`) **and** the PR author is in that issue's
assignees. Bots are exempt.

For the check to actually block merging, add it to "Required status checks"
in **Settings → Branches → Branch protection rules** for `main`.

## Pull requests

1. Open an issue (or pick an existing one) and ask a maintainer to assign it
   to you.
2. Branch from `main`. Use a short descriptive slug, e.g. `fix/quant-regex`
   or `feat/list-flag`.
3. Reference the issue in your PR description with `Fixes #N`, `Closes #N`,
   or `Resolves #N`. This is enforced by `check-issue.yml`.
4. Keep PRs focused — one logical change per PR.
5. Make sure `pre-commit run --all-files` is green before pushing.

## Releases

Releases are cut by pushing a git tag. `.github/workflows/publish.yml`
reacts to tags matching `*.*.*` or `v*`, builds `sdist` + `wheel`, and
uploads to PyPI via PyPA's
[trusted publishing](https://docs.pypi.org/trusted-publishers/) action.
No PyPI API token is stored in GitHub Secrets.

```bash
# 1. Bump the version in pyproject.toml (e.g. 0.0.0 -> 0.0.1)
# 2. Commit, tag, push
git commit -am "release 0.0.1"
git tag 0.0.1
git push origin main --tags
```

### One-time PyPI setup

1. Visit <https://pypi.org/manage/account/publishing/> → "Add a new pending
   publisher".
2. Fill in: Project name `hf2ollama`, Owner `wachawo`, Repository
   `hf2ollama`, Workflow `publish.yml`, Environment empty.
3. After the first successful release the publisher becomes permanent.

## Project layout

```
hf2ollama/
├── hf2ollama.py            # the script (single-module package)
├── pyproject.toml          # package metadata + tool configs
├── .pre-commit-config.yaml # black + ruff + mypy hooks
├── .github/workflows/
│   ├── ci.yml              # install + smoke + build on push/PR
│   ├── publish.yml         # build + upload to PyPI on tag
│   └── check-issue.yml     # PR must reference an issue assigned to author
├── docs/                   # localized READMEs (10 languages)
├── README.md               # English README
├── CONTRIBUTING.md         # this file
├── LICENSE                 # MIT
└── MANIFEST.in
```

## Reporting issues

Open an issue at <https://github.com/wachawo/hf2ollama/issues>. Include:

- the command you ran,
- the HuggingFace model id,
- the full error output (or a relevant excerpt),
- your `python --version` and OS.
