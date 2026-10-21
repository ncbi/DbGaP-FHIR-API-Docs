from __future__ import annotations

import logging
import re
from pathlib import Path
from unittest.mock import patch

import pytest
from helpers import drs_download_setup


@pytest.mark.parametrize(
    ("data_source", "source"), [("", "gap/phs000710"), (" SRA ", "sra/SRR21790641")]
)
def test_setup_uses_defaults_and_reads_the_passport(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    data_source: str,
    source: str,
) -> None:
    passport_text = "test-passport-é"
    passport_path = tmp_path / "passport-enc.txt"
    passport_path.write_text(f"  {passport_text}\n", encoding="utf-8")
    monkeypatch.chdir(tmp_path)

    with (
        patch.object(Path, "home", return_value=tmp_path),
        patch("builtins.input", side_effect=[data_source, "", "", ""]),
        patch.object(logging, "basicConfig"),
    ):
        config = drs_download_setup.configure_download()

    assert config.source == source
    assert config.output_directory == tmp_path / source
    assert config.output_directory.is_dir()
    assert config.passport_text == passport_text
    assert config.idx_base_url == "https://locate-beta.ncbi.nlm.nih.gov/idx/v2"
    assert config.drs_base_url == "https://locate-beta.ncbi.nlm.nih.gov/ga4gh/drs/v1"
    output = capsys.readouterr().out
    assert re.search(rf"\b{len(passport_text.encode()):,}\b", output)
    assert passport_text not in output


def test_setup_reprompts_for_source_and_accepts_custom_paths(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    passport_path = tmp_path / "custom-passport.txt"
    passport_path.write_text("test-passport", encoding="utf-8")
    output_directory = tmp_path / "custom" / "downloads"
    with (
        patch(
            "builtins.input",
            side_effect=[
                "invalid",
                " dbGaP ",
                " phs123456 ",
                f" {passport_path} ",
                f" {output_directory} ",
            ],
        ),
        patch.object(logging, "basicConfig"),
    ):
        config = drs_download_setup.configure_download()

    assert config.source == "gap/phs123456"
    assert config.output_directory == output_directory
    assert config.passport_text == "test-passport"
    assert output_directory.is_dir()
    assert "Please enter dbGaP or SRA." in capsys.readouterr().out


@pytest.mark.parametrize("relative_path", ["passport", "output directory"])
def test_setup_rejects_relative_paths(tmp_path: Path, relative_path: str) -> None:
    passport_path = (
        "relative-passport.txt" if relative_path == "passport" else str(tmp_path / "passport.txt")
    )
    with (
        patch("builtins.input", side_effect=["", "", passport_path, "relative-downloads"]),
        pytest.raises(ValueError, match=rf"The {relative_path} path must be absolute\."),
    ):
        drs_download_setup.configure_download()


def test_setup_reports_a_missing_passport(tmp_path: Path) -> None:
    with (
        patch(
            "builtins.input",
            side_effect=["", "", str(tmp_path / "missing.txt"), str(tmp_path / "downloads")],
        ),
        patch.object(logging, "basicConfig"),
        pytest.raises(FileNotFoundError),
    ):
        drs_download_setup.configure_download()
