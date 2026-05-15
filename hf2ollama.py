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
import time
import traceback
from pathlib import Path

from huggingface_hub import HfApi, snapshot_download
from huggingface_hub.utils import (
    GatedRepoError,
    HfHubHTTPError,
    RepositoryNotFoundError,
)

from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

LOGGING = {
    "handlers": [logging.StreamHandler()],
    "format": "%(asctime)s.%(msecs)03d [%(levelname)s]: (%(name)s) %(message)s",
    "level": logging.INFO,
    "datefmt": "%Y-%m-%d %H:%M:%S",
}
logging.basicConfig(**LOGGING)
logger = logging.getLogger(__name__)

HF_TOKEN = os.getenv("HF_TOKEN")
BASE_DIR = Path(__file__).resolve().parent
HF_DIR = BASE_DIR / "hf"
HF_CACHE_DIR = BASE_DIR / ".hf_cache"
LLAMA_CPP = BASE_DIR.parent / "llama.cpp"
LLAMA_REPO = "https://github.com/ggerganov/llama.cpp.git"
OUTTYPE = os.getenv("OUTTYPE", "f16")
QUANT_PRIORITY = ("Q4_K_M", "Q5_K_M", "Q4_K_S", "Q8_0", "Q5_0", "Q4_0", "F16", "BF16", "F32")

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


def _sibling_size(s) -> int:
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
    return sorted((s.rfilename, _sibling_size(s)) for s in info.siblings)


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


def ensure_llama_cpp() -> Path:
    """Clone llama.cpp once and install its conversion requirements."""
    if not LLAMA_CPP.exists():
        if not shutil.which("git"):
            raise RuntimeError("git is required but not found in PATH")
        logger.info(f"Cloning llama.cpp into {LLAMA_CPP}")
        subprocess.run(
            ["git", "clone", "--depth", "1", LLAMA_REPO, str(LLAMA_CPP)],
            check=True,
        )

    req = LLAMA_CPP / "requirements" / "requirements-convert_hf_to_gguf.txt"
    if req.exists():
        logger.info("Installing llama.cpp conversion requirements")
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "-q", "-r", str(req)],
            check=True,
        )

    convert = LLAMA_CPP / "convert_hf_to_gguf.py"
    if not convert.exists():
        raise FileNotFoundError(f"convert_hf_to_gguf.py not found in {LLAMA_CPP}")
    return convert


def download_model(model_id: str, quant: str | None = None) -> Path:
    """Download HF model snapshot to ./hf/<org>/<name>/.

    If `quant` is given, only `.gguf` files whose name contains that token plus
    small support files are downloaded — saves bandwidth and disk on `*-GGUF`
    repos that ship many quantizations.
    """
    if "/" not in model_id:
        raise ValueError(f"Model id must be in form 'org/name': {model_id}")
    org, name = model_id.split("/", 1)
    target = HF_DIR / org / name
    target.mkdir(parents=True, exist_ok=True)

    kwargs = dict(
        repo_id=model_id,
        local_dir=str(target),
        cache_dir=str(HF_CACHE_DIR / "hub"),
        token=HF_TOKEN or None,
    )
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


def convert_to_gguf(model_dir: Path, model_id: str, convert_script: Path) -> Path:
    """Convert HF model to GGUF placed next to its source files."""
    name = model_id.split("/", 1)[1]
    out_path = model_dir / f"{name}.{OUTTYPE}.gguf"
    logger.info(f"Converting to GGUF ({OUTTYPE}): {out_path}")
    subprocess.run(
        [
            sys.executable,
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


def write_modelfile(gguf_path: Path, model_id: str) -> Path:
    """Write a minimal Ollama Modelfile next to the GGUF file."""
    mf = gguf_path.parent / "Modelfile"
    mf.write_text(f"FROM {gguf_path}\n", encoding="utf-8")
    return mf


def derive_ollama_name(model_id: str) -> str:
    """org/name -> name (lowercased, ollama-friendly)."""
    name = model_id.split("/", 1)[1].lower()
    return name.replace("_", "-")


def main():
    parser = argparse.ArgumentParser(
        description="Download a HuggingFace model and convert it to GGUF for Ollama.",
    )
    parser.add_argument(
        "model_id",
        help="HuggingFace model id, e.g. PantheonUnbound/Satyr-V0.1-4B",
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
    args = parser.parse_args()

    model_id = args.model_id.strip()
    if "/" not in model_id:
        logger.error("Model id must be in form 'org/name'")
        sys.exit(2)

    if args.list:
        try:
            print_quant_list(model_id)
        except GatedRepoError:
            logger.error(
                f"Repository '{model_id}' is gated. Accept the license on the model page "
                f"and ensure HF_TOKEN in .env has access."
            )
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
                    logger.error(
                        f"--quant '{args.quant}' did not match any .gguf in {model_id}. "
                        f"Run with --list to see available quants."
                    )
                    sys.exit(1)
            else:
                logger.warning(
                    f"--quant ignored: {model_id} has no .gguf files (looks like a normal HF model)."
                )
                args.quant = None

        model_dir = download_model(model_id, quant=args.quant)
        existing = find_existing_ggufs(model_dir)
        config = model_dir / "config.json"

        if existing:
            gguf_path = pick_gguf(existing, preferred=args.quant)
            logger.info(
                f"Repo ships {len(existing)} GGUF file(s); using {gguf_path.name} (skipping conversion)"
            )
        elif config.exists():
            convert_script = ensure_llama_cpp()
            gguf_path = convert_to_gguf(model_dir, model_id, convert_script)
        else:
            logger.error(
                f"No config.json and no .gguf files in {model_dir}. "
                f"Repo may be empty, gated without access, or use an unsupported layout."
            )
            sys.exit(1)

        modelfile = write_modelfile(gguf_path, model_id)
    except GatedRepoError:
        logger.error(
            f"Repository '{model_id}' is gated. Accept the license on the model page "
            f"and ensure HF_TOKEN in .env has access."
        )
        sys.exit(1)
    except RepositoryNotFoundError:
        logger.error(
            f"Repository '{model_id}' not found on HuggingFace. "
            f"Check the spelling — some models (e.g. xAI Grok) are not published on HF."
        )
        sys.exit(1)
    except HfHubHTTPError as exc:
        logger.error(f"HuggingFace HTTP error: {type(exc).__name__}: {exc}")
        sys.exit(1)
    except subprocess.CalledProcessError as exc:
        logger.error(f"Subprocess failed (rc={exc.returncode}): {' '.join(exc.cmd)}")
        sys.exit(1)
    except Exception as exc:
        logger.error(f"{type(exc).__name__}: {exc}\n{traceback.format_exc()}")
        sys.exit(1)

    ollama_name = args.ollama_name or derive_ollama_name(model_id)

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
