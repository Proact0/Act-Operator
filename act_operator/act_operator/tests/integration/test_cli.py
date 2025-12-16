from __future__ import annotations

from pathlib import Path

from typer.testing import CliRunner

from act_operator.cli import app

runner = CliRunner()


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_init_creates_scaffold(tmp_path: Path) -> None:
    target_dir = tmp_path / "sample-act"

    result = runner.invoke(
        app,
        [
            "--path",
            str(target_dir),
            "--act-name",
            "Sample Act",
            "--cast-name",
            "Primary Cast",
            "--lang",
            "en",
        ],
    )
    assert result.exit_code == 0, result.stdout

    project_pyproject = target_dir / "pyproject.toml"
    cast_readme = target_dir / "casts" / "primary_cast" / "README.md"

    assert project_pyproject.exists()
    assert cast_readme.exists()
    assert "Sample Act" in _read(project_pyproject)
    assert "Primary Cast" in _read(cast_readme)


def test_init_derives_act_name_from_path(tmp_path: Path) -> None:
    target_dir = tmp_path / "custom-act"

    result = runner.invoke(
        app,
        [
            "--path",
            str(target_dir),
            "--cast-name",
            "Primary Cast",
            "--lang",
            "en",
        ],
    )
    assert result.exit_code == 0, result.stdout

    project_pyproject = target_dir / "pyproject.toml"
    assert "custom-act" in _read(project_pyproject)


def test_init_aborts_on_non_empty_dir(tmp_path: Path) -> None:
    target_dir = tmp_path / "existing"
    target_dir.mkdir()
    (target_dir / "existing.txt").write_text("data", encoding="utf-8")

    result = runner.invoke(
        app,
        [
            "--path",
            str(target_dir),
            "--cast-name",
            "Primary Cast",
            "--lang",
            "en",
        ],
    )

    assert result.exit_code != 0
    combined_output = (result.stdout or "") + (result.stderr or "")
    assert "The specified directory already exists and is not empty" in combined_output
