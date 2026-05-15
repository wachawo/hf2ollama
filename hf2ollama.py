#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Download a HuggingFace model and convert it to GGUF for Ollama."""

import argparse
import logging
import os
import re
import shutil
import subprocess
import sys
import traceback
from pathlib import Path
from typing import Any

from dotenv import find_dotenv, load_dotenv
from huggingface_hub import HfApi, snapshot_download
from huggingface_hub.utils import (
    GatedRepoError,
    HfHubHTTPError,
    RepositoryNotFoundError,
)

load_dotenv(find_dotenv())

LOGGING: dict[str, Any] = {
    "handlers": [logging.StreamHandler()],
    "format": "%(asctime)s.%(msecs)03d [%(levelname)s]: (%(name)s) %(message)s",
    "level": logging.INFO,
    "datefmt": "%Y-%m-%d %H:%M:%S",
}
logging.basicConfig(**LOGGING)
logger = logging.getLogger(__name__)

HF_TOKEN = os.getenv("HF_TOKEN")
# Workspace = current working directory. Works for both `python3 hf2ollama.py` from
# a checkout and `hf2ollama` from a pip-installed binary launched anywhere.
BASE_DIR = Path(os.getenv("HF2OLLAMA_WORKSPACE", str(Path.cwd()))).resolve()
HF_DIR = Path(os.getenv("HF2OLLAMA_HF_DIR", str(BASE_DIR / "hf"))).resolve()
HF_CACHE_DIR = Path(os.getenv("HF2OLLAMA_CACHE_DIR", str(BASE_DIR / ".hf_cache"))).resolve()
LLAMA_CPP = Path(os.getenv("HF2OLLAMA_LLAMA_CPP_DIR", str(BASE_DIR / "llama.cpp"))).resolve()
# Conversion deps (torch, transformers, sentencepiece, ...) are installed
# into an isolated venv inside the llama.cpp checkout to avoid polluting
# the user's interpreter. Overrideable via HF2OLLAMA_LLAMA_VENV.
LLAMA_VENV = Path(os.getenv("HF2OLLAMA_LLAMA_VENV", str(LLAMA_CPP / ".venv"))).resolve()
LLAMA_REPO = "https://github.com/ggerganov/llama.cpp.git"
# Branch, tag or 40-char SHA to clone. Defaults to "master" for convenience;
# set HF2OLLAMA_LLAMA_CPP_REF=<tag-or-sha> to pin to an audited revision.
LLAMA_REPO_REF = os.getenv("HF2OLLAMA_LLAMA_CPP_REF", "master")
OUTTYPE = os.getenv("OUTTYPE", "f16")
QUANT_PRIORITY = (
    "Q4_K_M",
    "Q5_K_M",
    "Q4_K_S",
    "Q8_0",
    "Q5_0",
    "Q4_0",
    "F16",
    "BF16",
    "F32",
)

# Keep all HuggingFace caches inside the project dir, not in ~/.cache/huggingface
os.environ.setdefault("HF_HOME", str(HF_CACHE_DIR))
os.environ.setdefault("HF_HUB_CACHE", str(HF_CACHE_DIR / "hub"))

IGNORE_PATTERNS = [
    "*.bin",
    "*.pth",
    "*.h5",
    "*.msgpack",
    "*.onnx",
    "consolidated.*",
    "original/*",
]

QUANT_ALLOW_PATTERNS = [
    "*.json",
    "*.txt",
    "*.md",
    "tokenizer*",
    "*.tiktoken",
    "*.model",
]

# HuggingFace repo names: [A-Za-z0-9][A-Za-z0-9._-]{0,95}. Reject anything else
# so model_id cannot become a path-traversal vector when joined with HF_DIR.
MODEL_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,95}/[A-Za-z0-9][A-Za-z0-9._-]{0,95}$")

# llama.cpp quant tokens look like Q4_K_M, IQ3_XXS, F16, BF16, ...
QUANT_ARG_RE = re.compile(r"^[A-Za-z0-9_]{1,32}$")

# Strip ASCII control chars (incl. ESC) so user-supplied values cannot inject
# ANSI sequences into the terminal when echoed back in errors/logs.
CONTROL_CHARS_RE = re.compile(r"[\x00-\x1f\x7f]")


def validate_model_id(model_id: str) -> None:
    """Reject model ids that do not match the HuggingFace owner/name shape."""
    if not MODEL_ID_RE.match(model_id):
        raise ValueError(f"Invalid model id (expected owner/name, alphanumerics plus '._-' only): {model_id!r}")


def validate_quant_arg(quant: str) -> None:
    """Reject --quant tokens that fall outside the alphanumeric/underscore shape."""
    if not QUANT_ARG_RE.match(quant):
        raise ValueError(f"Invalid --quant value (expected alphanumerics and '_' only): {quant!r}")


def safe(value: str) -> str:
    """Strip control characters so untrusted strings are safe to echo."""
    return CONTROL_CHARS_RE.sub("?", value)


def sibling_size(s: Any) -> int:
    """Best-effort size in bytes for a HuggingFace repo sibling object."""
    lfs = getattr(s, "lfs", None)
    if lfs is not None:
        size = getattr(lfs, "size", 0) or 0
        if size:
            return size
    return getattr(s, "size", 0) or 0


def list_repo_files(model_id: str) -> list[tuple[str, int]]:
    """Return [(filename, size_bytes)] for every file in the repo."""
    api = HfApi(token=HF_TOKEN or None)
    info = api.repo_info(model_id, files_metadata=True)
    siblings = getattr(info, "siblings", None) or []
    return sorted((s.rfilename, sibling_size(s)) for s in siblings)


def list_repo_ggufs(model_id: str) -> list[tuple[str, int]]:
    """Return [(filename, size_bytes)] for every .gguf file in the repo."""
    return [(n, s) for n, s in list_repo_files(model_id) if n.lower().endswith(".gguf")]


def human_size(n: int) -> str:
    if not n:
        return "?"
    f = float(n)
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if f < 1024:
            return f"{f:.1f} {unit}"
        f /= 1024
    return f"{f:.1f} PB"


WEIGHT_EXTS = (".gguf", ".safetensors", ".bin", ".pth", ".onnx", ".h5", ".msgpack")

QUANT_RE = re.compile(
    r"(IQ\d+(?:_[A-Z0-9]+)*|Q\d+(?:_[A-Z0-9]+)*|BF16|F16|F32)",
    re.IGNORECASE,
)


def extract_quant_token(filename: str) -> str:
    """Pull the quant token (Q4_K_M, IQ3_XXS, F16, ...) out of a GGUF filename."""
    m = QUANT_RE.search(filename)
    return m.group(1).upper() if m else "?"


def print_quant_list(model_id: str) -> None:
    files = list_repo_files(model_id)
    ggufs = [(n, s) for n, s in files if n.lower().endswith(".gguf")]

    if ggufs:
        rows = [(n, human_size(s), extract_quant_token(n), s) for n, s in ggufs]
        name_w = max(len(n) for n, _, _, _ in rows)
        size_w = max(len(s) for _, s, _, _ in rows)
        print(f"{model_id} — available GGUF files:")
        total = 0
        for name, size_h, token, raw in rows:
            print(f"  {name:<{name_w}}   {size_h:>{size_w}}   {token}")
            total += raw
        print()
        print(f"Total if all downloaded: {human_size(total)}")
        print("Pick one with:  --quant <token>   e.g.  --quant Q4_K_M")
        return

    weights = [(n, s) for n, s in files if n.lower().endswith(WEIGHT_EXTS)]
    if weights:
        print(f"{model_id} — normal HF model (no prebuilt GGUF in repo).")
        print("Weight files:")
        name_w = max(len(n) for n, _ in weights)
        total = 0
        for name, size in weights:
            print(f"  {name:<{name_w}}   {human_size(size)}")
            total += size
        print()
        print(f"Total download size: ~{human_size(total)}")
        print("Run without --list/--quant to download and convert to GGUF via llama.cpp.")
        return

    print(f"{model_id}: repo has no weight files (.gguf / .safetensors / .bin / ...).")
    print("Probably an adapter, dataset, or empty placeholder repo.")


def print_dry_run_plan(model_id: str, quant: str | None, ollama_name_arg: str | None) -> None:
    """Print the actions that would be taken for ``model_id`` without executing them."""
    org, name = model_id.split("/", 1)
    target = HF_DIR / org / name
    files = list_repo_files(model_id)
    ggufs = [(n, s) for n, s in files if n.lower().endswith(".gguf")]
    has_config = any(n == "config.json" for n, _ in files)

    print("DRY RUN — the following actions would be performed:")
    print()
    print(f"  Workspace:   {BASE_DIR}")
    print(f"  Snapshot to: {target}")

    if quant:
        matching = [(n, s) for n, s in ggufs if quant.lower() in n.lower()]
        total = sum(s for _, s in matching)
        print(f"  Download:    {len(matching)} .gguf file(s) matching {quant!r}  (~{human_size(total)})")
        for n, s in matching:
            print(f"               - {n}   {human_size(s)}")
    elif ggufs:
        total = sum(s for _, s in ggufs)
        print(f"  Download:    {len(ggufs)} .gguf file(s) shipped by the repo  (~{human_size(total)})")
    else:
        weights = [(n, s) for n, s in files if n.lower().endswith(WEIGHT_EXTS)]
        total = sum(s for _, s in weights)
        print(f"  Download:    HF snapshot (excluding {', '.join(IGNORE_PATTERNS)})  (~{human_size(total)} of weights)")

    needs_conversion = not ggufs and has_config
    if needs_conversion:
        print(f"  Conversion:  required — clone llama.cpp@{LLAMA_REPO_REF} into {LLAMA_CPP}")
        print(f"               create isolated venv at {LLAMA_VENV}")
        print("               pip install -r llama.cpp/requirements/requirements-convert_hf_to_gguf.txt (into the venv only)")
        print(f"               run convert_hf_to_gguf.py --outtype {OUTTYPE}")
    elif ggufs:
        chosen = pick_gguf([Path(n) for n, _ in (matching if quant else ggufs)], preferred=quant) if (matching if quant else ggufs) else None
        if chosen:
            print(f"  Conversion:  skipped — would use {chosen.name}")
    else:
        print("  Conversion:  cannot proceed — repo has no .gguf and no config.json")

    print(f"  Modelfile:   would be written to {target}/Modelfile")
    ollama_name = safe(ollama_name_arg) if ollama_name_arg else derive_ollama_name(model_id)
    print()
    print("Final commands you would run:")
    print(f"  ollama create {ollama_name} -f {target}/Modelfile")
    print(f"  ollama run {ollama_name}")


def venv_python(venv: Path) -> Path:
    """Return the path to the python interpreter inside a venv."""
    return venv / ("Scripts" if os.name == "nt" else "bin") / ("python.exe" if os.name == "nt" else "python")


def ensure_llama_cpp() -> tuple[Path, Path]:
    """Ensure a usable llama.cpp checkout and isolated venv are available.

    Returns ``(convert_script, python_executable)``. The python executable
    lives in a dedicated venv at ``LLAMA_VENV`` so conversion deps
    (torch, transformers, sentencepiece, ...) never touch the user's
    interpreter.
    """
    convert = LLAMA_CPP / "convert_hf_to_gguf.py"

    if not LLAMA_CPP.exists():
        if not shutil.which("git"):
            raise RuntimeError(
                "llama.cpp is required for converting this model, but no clone was found "
                f"at {LLAMA_CPP} and 'git' is not in PATH.\n"
                "Either install git so the script can clone it, or point "
                "HF2OLLAMA_LLAMA_CPP_DIR at an existing llama.cpp checkout."
            )
        logger.info(f"Cloning llama.cpp ({LLAMA_REPO_REF}) into {LLAMA_CPP}")
        subprocess.run(
            ["git", "clone", "--depth", "1", "--branch", LLAMA_REPO_REF, LLAMA_REPO, str(LLAMA_CPP)],
            check=True,
            timeout=600,
        )

    if not convert.exists():
        raise FileNotFoundError(
            f"{convert} not found. {LLAMA_CPP} does not look like a llama.cpp checkout.\n" "Delete that directory and rerun, or set HF2OLLAMA_LLAMA_CPP_DIR to a working clone."
        )

    # If the checkout has git metadata, surface the resolved commit so a
    # compromised upstream is easier to spot. Users may also point at a
    # tarball-extracted directory with no .git/ — skip the lookup in that case.
    if shutil.which("git") and (LLAMA_CPP / ".git").exists():
        sha = subprocess.check_output(
            ["git", "-C", str(LLAMA_CPP), "rev-parse", "HEAD"],
            text=True,
            timeout=30,
        ).strip()
        logger.info(f"llama.cpp at {sha} ({LLAMA_REPO_REF})")
    else:
        logger.info(f"Using llama.cpp at {LLAMA_CPP} (no git metadata, commit unknown)")

    python_bin = venv_python(LLAMA_VENV)
    if not python_bin.exists():
        logger.info(f"Creating isolated venv for llama.cpp at {LLAMA_VENV}")
        subprocess.run(
            [sys.executable, "-m", "venv", str(LLAMA_VENV)],
            check=True,
            timeout=300,
        )
        # Upgrade pip inside the venv once — old pip versions choke on some wheels.
        subprocess.run(
            [str(python_bin), "-m", "pip", "install", "-q", "--upgrade", "pip"],
            check=True,
            timeout=300,
        )

    req = LLAMA_CPP / "requirements" / "requirements-convert_hf_to_gguf.txt"
    if req.exists():
        marker = LLAMA_VENV / ".hf2ollama-deps-installed"
        if not marker.exists() or marker.stat().st_mtime < req.stat().st_mtime:
            logger.info(f"Installing llama.cpp conversion requirements into {LLAMA_VENV}")
            subprocess.run(
                [str(python_bin), "-m", "pip", "install", "-q", "-r", str(req)],
                check=True,
                timeout=900,
            )
            marker.touch()

    return convert, python_bin


def download_model(model_id: str, quant: str | None = None) -> Path:
    """Download HF model snapshot to ./hf/<org>/<name>/.

    If `quant` is given, only `.gguf` files whose name contains that token plus
    small support files are downloaded — saves bandwidth and disk on `*-GGUF`
    repos that ship many quantizations.
    """
    validate_model_id(model_id)
    org, name = model_id.split("/", 1)
    target = HF_DIR / org / name
    target.mkdir(parents=True, exist_ok=True)

    kwargs: dict[str, Any] = {
        "repo_id": model_id,
        "local_dir": str(target),
        "cache_dir": str(HF_CACHE_DIR / "hub"),
        "token": HF_TOKEN or None,
    }
    if quant:
        logger.info(f"Downloading {model_id} (quant={quant}) -> {target}")
        kwargs["allow_patterns"] = [f"*{quant}*.gguf", *QUANT_ALLOW_PATTERNS]
    else:
        logger.info(f"Downloading {model_id} -> {target}")
        kwargs["ignore_patterns"] = IGNORE_PATTERNS

    snapshot_download(**kwargs)
    return target


def find_existing_ggufs(model_dir: Path) -> list[Path]:
    """Return .gguf files shipped by the repo itself (not our own outputs)."""
    return sorted(p for p in model_dir.glob("*.gguf") if p.is_file())


def pick_gguf(ggufs: list[Path], preferred: str | None = None) -> Path:
    """Pick a single GGUF from those available, preferring a given quant."""
    if preferred:
        for p in ggufs:
            if preferred.lower() in p.name.lower():
                return p
    for q in QUANT_PRIORITY:
        for p in ggufs:
            if q.lower() in p.name.lower():
                return p
    return ggufs[0]


def convert_to_gguf(model_dir: Path, model_id: str, convert_script: Path, python_bin: Path) -> Path:
    """Convert HF model to GGUF placed next to its source files."""
    name = model_id.split("/", 1)[1]
    out_path = model_dir / f"{name}.{OUTTYPE}.gguf"
    logger.info(f"Converting to GGUF ({OUTTYPE}): {out_path}")
    subprocess.run(
        [
            str(python_bin),
            str(convert_script),
            str(model_dir),
            "--outfile",
            str(out_path),
            "--outtype",
            OUTTYPE,
        ],
        check=True,
    )
    return out_path


def write_modelfile(gguf_path: Path) -> Path:
    """Write a minimal Ollama Modelfile next to the GGUF file."""
    mf = gguf_path.parent / "Modelfile"
    mf.write_text(f"FROM {gguf_path}\n", encoding="utf-8")
    return mf


def derive_ollama_name(model_id: str) -> str:
    """org/name -> name (lowercased, ollama-friendly)."""
    name = model_id.split("/", 1)[1].lower()
    return name.replace("_", "-")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Download a HuggingFace model and convert it to GGUF for Ollama.",
    )
    parser.add_argument(
        "model_id",
        help="HuggingFace model id, e.g. SicariusSicariiStuff/Assistant_Pepe_70B",
    )
    parser.add_argument(
        "--ollama-name",
        default=None,
        help="Override Ollama model name (default: derived from repo name)",
    )
    parser.add_argument(
        "--quant",
        default=None,
        help="Download/pick only this quant when the repo ships multiple GGUFs (e.g. Q4_K_M)",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List available .gguf files in the repo (with sizes) and exit",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the planned actions (clone, venv, download, convert) without executing them",
    )
    args = parser.parse_args()

    model_id = args.model_id.strip()
    try:
        validate_model_id(model_id)
    except ValueError as exc:
        logger.error(safe(str(exc)))
        sys.exit(2)

    if args.quant is not None:
        try:
            validate_quant_arg(args.quant)
        except ValueError as exc:
            logger.error(safe(str(exc)))
            sys.exit(2)

    if args.list:
        try:
            print_quant_list(model_id)
        except GatedRepoError:
            logger.error(f"Repository '{model_id}' is gated. Accept the license on the model page and ensure HF_TOKEN in .env has access.")
            sys.exit(1)
        except RepositoryNotFoundError:
            logger.error(f"Repository '{model_id}' not found on HuggingFace.")
            sys.exit(1)
        return

    try:
        if args.quant:
            repo_ggufs = list_repo_ggufs(model_id)
            if repo_ggufs:
                matches = [n for n, _ in repo_ggufs if args.quant.lower() in n.lower()]
                if not matches:
                    logger.error(f"--quant '{args.quant}' did not match any .gguf in {model_id}. Run with --list to see available quants.")
                    sys.exit(1)
            else:
                logger.warning(f"--quant ignored: {model_id} has no .gguf files (looks like a normal HF model).")
                args.quant = None

        if args.dry_run:
            print_dry_run_plan(model_id, args.quant, args.ollama_name)
            return

        model_dir = download_model(model_id, quant=args.quant)
        existing = find_existing_ggufs(model_dir)
        config = model_dir / "config.json"

        if existing:
            gguf_path = pick_gguf(existing, preferred=args.quant)
            logger.info(f"Repo ships {len(existing)} GGUF file(s); using {gguf_path.name} (skipping conversion)")
        elif config.exists():
            convert_script, python_bin = ensure_llama_cpp()
            gguf_path = convert_to_gguf(model_dir, model_id, convert_script, python_bin)
        else:
            logger.error(f"No config.json and no .gguf files in {model_dir}. Repo may be empty, gated without access, or use an unsupported layout.")
            sys.exit(1)

        modelfile = write_modelfile(gguf_path)
    except GatedRepoError:
        logger.error(f"Repository '{model_id}' is gated. Accept the license on the model page and ensure HF_TOKEN in .env has access.")
        sys.exit(1)
    except RepositoryNotFoundError:
        logger.error(f"Repository '{model_id}' not found on HuggingFace. Check the spelling — some models (e.g. xAI Grok) are not published on HF.")
        sys.exit(1)
    except HfHubHTTPError as exc:
        logger.error(f"HuggingFace HTTP error: {type(exc).__name__}: {exc}")
        sys.exit(1)
    except subprocess.CalledProcessError as exc:
        logger.error(f"Subprocess failed (rc={exc.returncode}): {' '.join(exc.cmd)}")
        sys.exit(1)
    except subprocess.TimeoutExpired as exc:
        cmd = exc.cmd if isinstance(exc.cmd, str) else " ".join(str(c) for c in exc.cmd)
        logger.error(f"Subprocess timed out after {exc.timeout}s: {cmd}")
        sys.exit(1)
    except (FileNotFoundError, RuntimeError) as exc:
        # Missing prerequisite (git, llama.cpp checkout, conversion script).
        # The message itself is actionable — no traceback needed.
        logger.error(str(exc))
        sys.exit(1)
    except Exception as exc:
        logger.error(f"{type(exc).__name__}: {exc}\n{traceback.format_exc()}")
        sys.exit(1)

    ollama_name = safe(args.ollama_name) if args.ollama_name else derive_ollama_name(model_id)

    # Let background tqdm bars from huggingface_hub finish flushing before our final block.
    sys.stderr.flush()
    sys.stdout.flush()

    print(flush=True)
    print("=" * 70, flush=True)
    print(f"GGUF:      {gguf_path}", flush=True)
    print(f"Modelfile: {modelfile}", flush=True)
    print(flush=True)
    print("Done. To import the model into Ollama, run these 2 commands:", flush=True)
    print(f"  ollama create {ollama_name} -f {modelfile}", flush=True)
    print(f"  ollama run {ollama_name}", flush=True)
    print("=" * 70, flush=True)


if __name__ == "__main__":
    main()
