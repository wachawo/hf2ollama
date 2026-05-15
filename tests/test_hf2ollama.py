#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Unit tests for the pure helpers in hf2ollama.

Anything that talks to the network (HfApi, snapshot_download) or shells
out (git, llama.cpp) is intentionally not tested here — those paths
belong in an integration suite.
"""

import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

import hf2ollama as h

SCRIPT = Path(h.__file__).resolve()


class TestValidateModelId:
    @pytest.mark.parametrize(
        "model_id",
        [
            "meta-llama/Llama-3.2-1B",
            "Qwen/Qwen2.5-7B-Instruct",
            "SicariusSicariiStuff/Assistant_Pepe_70B",
            "a/b",
            "Org.Name/Model.v1",
        ],
    )
    def test_accepts_valid(self, model_id: str) -> None:
        h.validate_model_id(model_id)

    @pytest.mark.parametrize(
        "model_id",
        [
            "",
            "no-slash",
            "/leading-slash",
            "trailing/",
            "two/slashes/here",
            "owner/name with space",
            "owner/name;rm -rf /",
            "../etc/passwd",
            "owner/" + "a" * 200,
            "-leading-dash/name",
            "owner/.hidden",
        ],
    )
    def test_rejects_invalid(self, model_id: str) -> None:
        with pytest.raises(ValueError):
            h.validate_model_id(model_id)


class TestValidateQuantArg:
    @pytest.mark.parametrize("q", ["Q4_K_M", "IQ3_XXS", "F16", "BF16", "Q8_0", "f32"])
    def test_accepts_valid(self, q: str) -> None:
        h.validate_quant_arg(q)

    @pytest.mark.parametrize("q", ["", "Q4 K M", "Q4-K-M", "Q4;rm", "x" * 33, "Q4/K"])
    def test_rejects_invalid(self, q: str) -> None:
        with pytest.raises(ValueError):
            h.validate_quant_arg(q)


class TestValidateOuttype:
    @pytest.mark.parametrize("v", ["f16", "f32", "bf16", "q8_0", "auto"])
    def test_accepts_valid(self, v: str) -> None:
        h.validate_outtype(v)

    @pytest.mark.parametrize("v", ["", "F16", "fp16", "q4_k_m", "auto ", "q8", "garbage"])
    def test_rejects_invalid(self, v: str) -> None:
        with pytest.raises(ValueError):
            h.validate_outtype(v)


class TestSafe:
    def test_strips_control_chars(self) -> None:
        assert h.safe("hello\x00world") == "hello?world"

    def test_strips_escape_sequence(self) -> None:
        assert h.safe("\x1b[31mred\x1b[0m") == "?[31mred?[0m"

    def test_keeps_printable(self) -> None:
        s = "Q4_K_M/owner-name.v1"
        assert h.safe(s) == s

    def test_strips_del(self) -> None:
        assert h.safe("a\x7fb") == "a?b"


class TestSiblingSize:
    def test_prefers_lfs_size(self) -> None:
        sib = SimpleNamespace(lfs=SimpleNamespace(size=1234), size=99)
        assert h.sibling_size(sib) == 1234

    def test_falls_back_to_size(self) -> None:
        sib = SimpleNamespace(lfs=None, size=42)
        assert h.sibling_size(sib) == 42

    def test_lfs_with_zero_size_falls_back(self) -> None:
        sib = SimpleNamespace(lfs=SimpleNamespace(size=0), size=7)
        assert h.sibling_size(sib) == 7

    def test_no_attrs(self) -> None:
        assert h.sibling_size(SimpleNamespace()) == 0


class TestHumanSize:
    @pytest.mark.parametrize(
        "n,expected",
        [
            (0, "?"),
            (1, "1.0 B"),
            (1023, "1023.0 B"),
            (1024, "1.0 KB"),
            (1024 * 1024, "1.0 MB"),
            (1024 * 1024 * 1024, "1.0 GB"),
            (1024**4, "1.0 TB"),
            (1024**5, "1.0 PB"),
        ],
    )
    def test_formatting(self, n: int, expected: str) -> None:
        assert h.human_size(n) == expected


class TestExtractQuantToken:
    @pytest.mark.parametrize(
        "filename,expected",
        [
            ("model.Q4_K_M.gguf", "Q4_K_M"),
            ("Model-IQ3_XXS.gguf", "IQ3_XXS"),
            ("Model.F16.gguf", "F16"),
            ("foo.bf16.gguf", "BF16"),
            ("foo.f32.gguf", "F32"),
            ("model.q8_0.gguf", "Q8_0"),
            ("no-token.gguf", "?"),
        ],
    )
    def test_extracts(self, filename: str, expected: str) -> None:
        assert h.extract_quant_token(filename) == expected


class TestPickGguf:
    def test_preferred_match_wins(self, tmp_path: Path) -> None:
        files = [tmp_path / "m.Q8_0.gguf", tmp_path / "m.Q4_K_M.gguf", tmp_path / "m.F16.gguf"]
        assert h.pick_gguf(files, preferred="Q4_K_M") == files[1]

    def test_preferred_case_insensitive(self, tmp_path: Path) -> None:
        files = [tmp_path / "m.Q4_K_M.gguf"]
        assert h.pick_gguf(files, preferred="q4_k_m") == files[0]

    def test_priority_fallback(self, tmp_path: Path) -> None:
        # Q4_K_M is highest priority; should be chosen even with no preference.
        files = [tmp_path / "m.Q8_0.gguf", tmp_path / "m.Q4_K_M.gguf", tmp_path / "m.F16.gguf"]
        assert h.pick_gguf(files) == files[1]

    def test_no_priority_match_returns_first(self, tmp_path: Path) -> None:
        files = [tmp_path / "weird-XYZ.gguf", tmp_path / "other-ABC.gguf"]
        assert h.pick_gguf(files) == files[0]

    def test_preferred_miss_falls_back_to_priority(self, tmp_path: Path) -> None:
        files = [tmp_path / "m.Q8_0.gguf", tmp_path / "m.F16.gguf"]
        # preferred="Q4_K_M" not present → priority order picks Q8_0 over F16.
        assert h.pick_gguf(files, preferred="Q4_K_M") == files[0]


class TestDeriveOllamaName:
    @pytest.mark.parametrize(
        "model_id,expected",
        [
            ("meta-llama/Llama-3.2-1B", "llama-3.2-1b"),
            ("SicariusSicariiStuff/Assistant_Pepe_70B", "assistant-pepe-70b"),
            ("Qwen/Qwen2.5-7B-Instruct", "qwen2.5-7b-instruct"),
            ("owner/UPPER_CASE_NAME", "upper-case-name"),
        ],
    )
    def test_derives(self, model_id: str, expected: str) -> None:
        assert h.derive_ollama_name(model_id) == expected


class TestWriteModelfile:
    def test_writes_from_line(self, tmp_path: Path) -> None:
        gguf = tmp_path / "model.f16.gguf"
        gguf.touch()
        mf = h.write_modelfile(gguf)
        assert mf == tmp_path / "Modelfile"
        assert mf.read_text(encoding="utf-8") == f"FROM {gguf}\n"

    def test_overwrites_existing(self, tmp_path: Path) -> None:
        gguf = tmp_path / "model.gguf"
        gguf.touch()
        (tmp_path / "Modelfile").write_text("stale", encoding="utf-8")
        h.write_modelfile(gguf)
        assert (tmp_path / "Modelfile").read_text(encoding="utf-8") == f"FROM {gguf}\n"


class TestFindExistingGgufs:
    def test_returns_only_gguf_sorted(self, tmp_path: Path) -> None:
        names = ["b.gguf", "a.gguf", "config.json", "model.safetensors", "weights.bin"]
        for n in names:
            (tmp_path / n).write_text("", encoding="utf-8")
        found = h.find_existing_ggufs(tmp_path)
        assert [p.name for p in found] == ["a.gguf", "b.gguf"]

    def test_skips_directories_with_gguf_suffix(self, tmp_path: Path) -> None:
        (tmp_path / "real.gguf").write_text("", encoding="utf-8")
        (tmp_path / "fake.gguf").mkdir()
        found = h.find_existing_ggufs(tmp_path)
        assert [p.name for p in found] == ["real.gguf"]

    def test_empty_dir(self, tmp_path: Path) -> None:
        assert h.find_existing_ggufs(tmp_path) == []


class TestInitState:
    def test_is_active_venv_returns_bool(self) -> None:
        # We don't assert True/False — pytest may run inside or outside a venv.
        # We just verify the function returns a real bool, not None/raise.
        assert isinstance(h.is_active_venv(), bool)

    def test_load_initialized_python_missing(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(h, "STATE_FILE", tmp_path / "no-such-file")
        assert h.load_initialized_python() is None

    def test_load_initialized_python_empty(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        state = tmp_path / "state"
        state.write_text("\n", encoding="utf-8")
        monkeypatch.setattr(h, "STATE_FILE", state)
        assert h.load_initialized_python() is None

    def test_load_initialized_python_stale(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        state = tmp_path / "state"
        state.write_text(str(tmp_path / "does-not-exist") + "\n", encoding="utf-8")
        monkeypatch.setattr(h, "STATE_FILE", state)
        assert h.load_initialized_python() is None

    def test_load_initialized_python_valid(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        py = tmp_path / "fake-python"
        py.touch()
        state = tmp_path / "state"
        state.write_text(str(py) + "\n", encoding="utf-8")
        monkeypatch.setattr(h, "STATE_FILE", state)
        assert h.load_initialized_python() == py


class TestCli:
    """Subprocess-level smoke tests for the actual CLI entry point."""

    def test_help_exits_zero(self) -> None:
        r = subprocess.run([sys.executable, str(SCRIPT), "--help"], capture_output=True, text=True, timeout=30)
        assert r.returncode == 0
        assert "usage" in r.stdout.lower()
        assert "model_id" in r.stdout

    def test_bad_model_id_exits_two(self) -> None:
        r = subprocess.run([sys.executable, str(SCRIPT), "bogus-no-slash"], capture_output=True, text=True, timeout=30)
        assert r.returncode == 2
        assert "invalid model id" in r.stderr.lower()
