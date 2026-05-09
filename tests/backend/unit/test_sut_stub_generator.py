"""Unit tests for scripts/generate_sut_stubs.py (meta; not agent-generated)."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

# Repo root: .../level8
REPO_ROOT = Path(__file__).resolve().parents[3]
GEN = REPO_ROOT / "scripts" / "generate_sut_stubs.py"


def _run_generator(repo: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(GEN), "--repo-root", str(repo)],
        capture_output=True,
        text=True,
        check=False,
    )


def test_generates_function_stub(tmp_path: Path) -> None:
    tests = tmp_path / "tests" / "backend" / "unit"
    tests.mkdir(parents=True)
    app = tmp_path / "src" / "backend" / "app"
    app.mkdir(parents=True)
    (app / "__init__.py").write_text('"""app."""\n', encoding="utf-8")

    (tests / "test_widget.py").write_text(
        "from app.widget import do_thing\n\n"
        "def test_do_thing():\n"
        "    assert do_thing() == 1\n",
        encoding="utf-8",
    )

    cp = _run_generator(tmp_path)
    assert cp.returncode == 0, cp.stderr + cp.stdout

    stub = app / "widget.py"
    assert stub.is_file()
    text = stub.read_text(encoding="utf-8")
    assert "def do_thing" in text
    assert "NotImplementedError" in text
    assert "SUT stub — implement in agent-2-codegen" in text


def test_idempotent_second_run(tmp_path: Path) -> None:
    tests = tmp_path / "tests" / "backend" / "unit"
    tests.mkdir(parents=True)
    app = tmp_path / "src" / "backend" / "app"
    app.mkdir(parents=True)
    (app / "__init__.py").write_text('"""app."""\n', encoding="utf-8")
    (tests / "test_x.py").write_text(
        "from app.alpha import run\n\ndef test_run():\n    assert run() is None\n",
        encoding="utf-8",
    )

    assert _run_generator(tmp_path).returncode == 0
    first = (app / "alpha.py").read_text(encoding="utf-8")
    assert _run_generator(tmp_path).returncode == 0
    second = (app / "alpha.py").read_text(encoding="utf-8")
    assert first == second


def test_rejects_class_import_name(tmp_path: Path) -> None:
    tests = tmp_path / "tests" / "backend" / "unit"
    tests.mkdir(parents=True)
    app = tmp_path / "src" / "backend" / "app"
    app.mkdir(parents=True)
    (app / "__init__.py").write_text('"""app."""\n', encoding="utf-8")
    (tests / "test_bad.py").write_text(
        "from app.bad import BadClass\n\ndef test_x():\n    assert BadClass\n",
        encoding="utf-8",
    )

    cp = _run_generator(tmp_path)
    assert cp.returncode == 1
    assert "class stubs are Phase 1b" in cp.stderr


def test_skips_contract_directory(tmp_path: Path) -> None:
    tests = tmp_path / "tests" / "backend" / "contract"
    tests.mkdir(parents=True)
    app = tmp_path / "src" / "backend" / "app"
    app.mkdir(parents=True)
    (app / "__init__.py").write_text('"""app."""\n', encoding="utf-8")
    (tests / "test_contract.py").write_text(
        "from app.secret import x\n",
        encoding="utf-8",
    )

    cp = _run_generator(tmp_path)
    assert cp.returncode == 0
    assert not (app / "secret.py").exists()
