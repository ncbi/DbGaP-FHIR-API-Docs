from __future__ import annotations

import json
import logging
import re
from collections.abc import Callable
from datetime import datetime
from pathlib import Path
from types import SimpleNamespace
from typing import TYPE_CHECKING, cast
from unittest.mock import MagicMock, call, patch

import requests

if TYPE_CHECKING:
    import pytest

NOTEBOOK_PATH = (
    Path(__file__).resolve().parents[1] / "download_all_dbGaP_phenotype_dataset_demo.ipynb"
)

CONFIGURATION_CELL_ID = "configuration"
MANIFEST_REQUEST_CELL_ID = "retrieve-manifest"
DOWNLOAD_FUNCTION_CELL_ID = "download-drs-object"
DOWNLOAD_LOOP_CELL_ID = "download-manifest-contents"

NotebookScope = dict[str, object]
DownloadFunction = Callable[[str, Path, int, int], float | None]


def assert_matches(regex: str | re.Pattern[str], actual: str) -> None:
    """Assert that a regular expression occurs within a string.

    Args:
        regex: Regular expression string or compiled pattern to search for.
        actual: String in which to search.

    Raises:
        AssertionError: Raised with the pattern and actual text when there is no match.
    """
    if re.search(regex, actual) is None:
        raise AssertionError(f"Regex {regex!r} did not match:\n{actual}")


def assert_contains(needle: object, haystack: str) -> None:
    """Assert that an object's string representation occurs within a string.

    Args:
        needle: Object whose string representation to search for.
        haystack: String in which to search.

    Raises:
        AssertionError: Raised when ``needle`` is not present in ``haystack``.
    """
    s = str(needle)
    try:
        assert_matches(re.escape(s), haystack)
    except AssertionError as e:
        raise AssertionError(f"{s!r} was not found in:\n{haystack}") from e


def notebook_code(cell_id: str) -> str:
    """Return the source for exactly one cell in the demo notebook.

    Args:
        cell_id: Identifier of the notebook cell to load. Its ``id`` field.

    Returns:
        The cell's source lines concatenated into one string. Newlines in the
        source are not stripped and will persist within the resulting string.

    Raises:
        OSError: Raised when the notebook file cannot be read.
        UnicodeError: Raised when the notebook cannot be decoded as UTF-8.
        json.JSONDecodeError: Raised when the notebook does not contain valid JSON.
        AssertionError: Raised when ``cell_id`` does not identify exactly one cell.
        AttributeError: Raised when a notebook cell is not a JSON object.
        KeyError: Raised when the notebook or matching cell lacks a required field.
        TypeError: Raised when the notebook structure or cell source has an unexpected type.
    """
    notebook = json.loads(NOTEBOOK_PATH.read_text(encoding="utf-8"))
    matching_cells = [cell for cell in notebook["cells"] if cell.get("id") == cell_id]
    assert len(matching_cells) == 1
    return "".join(matching_cells[0]["source"])


def execute_notebook_cell(cell_id: str, scope: NotebookScope) -> None:
    """Execute one repository-owned notebook cell in a shared namespace.

    Args:
        cell_id: Human-readable identifier of the notebook cell to execute.
        scope: Globals namespace shared with the executed cell.
            (Modified by function)

    Returns:
        None.

    Raises:
        OSError: Raised when the notebook file cannot be read.
        UnicodeError: Raised when the notebook cannot be decoded as UTF-8.
        json.JSONDecodeError: Raised when the notebook does not contain valid JSON.
        AssertionError: Raised when ``cell_id`` does not identify exactly one cell.
        AttributeError: Raised when a notebook cell is not a JSON object.
        KeyError: Raised when the notebook or matching cell lacks a required field.
        TypeError: Raised when the notebook structure or cell source has an unexpected type.
        SyntaxError: Raised when the selected cell cannot be compiled.
        Exception: Raised when executing the selected cell raises another exception.
    """
    exec(  # noqa: S102 - the source is a repository-owned notebook under test
        compile(notebook_code(cell_id), f"<notebook:{cell_id}>", "exec"),
        scope,
    )


def define_download_function() -> DownloadFunction:
    """Load the notebook's DRS download function into an isolated test scope.

    Returns:
        The ``dl_drs_id_to_file`` function defined by the notebook.

    Raises:
        OSError: Raised when the notebook file cannot be read.
        UnicodeError: Raised when the notebook cannot be decoded as UTF-8.
        json.JSONDecodeError: Raised when the notebook does not contain valid JSON.
        AssertionError: Raised when the download-function cell cannot be uniquely identified.
        AttributeError: Raised when a notebook cell is not a JSON object.
        KeyError: Raised when required notebook fields or ``dl_drs_id_to_file`` are absent.
        TypeError: Raised when the notebook structure or cell source has an unexpected type.
        SyntaxError: Raised when the download-function cell cannot be compiled.
        Exception: Raised when executing the download-function cell raises another exception.
    """
    scope: NotebookScope = {
        "Path": Path,
        "config": SimpleNamespace(
            drs_base_url="https://drs.example.test/ga4gh/drs/v1",
            passport_text="test-passport",
        ),
        "datetime": datetime,
        "json": json,
        "logging": logging,
        "requests": requests,
    }
    execute_notebook_cell(DOWNLOAD_FUNCTION_CELL_ID, scope)
    return cast(DownloadFunction, scope["dl_drs_id_to_file"])


def test_notebook_does_not_store_execution_results() -> None:
    notebook = json.loads(NOTEBOOK_PATH.read_text(encoding="utf-8"))
    cell_ids = [cell["id"] for cell in notebook["cells"]]
    assert len(cell_ids) == len(set(cell_ids))
    assert all(re.fullmatch(r"[a-z]+(?:-[a-z]+)*", cell_id) for cell_id in cell_ids)
    for cell in notebook["cells"]:
        assert cell["metadata"] == {}
        if cell["cell_type"] == "code":
            assert cell["execution_count"] is None
            assert cell["outputs"] == []


def test_configuration_uses_the_interactive_setup_helper(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    output_directory = tmp_path / "downloads"
    passport_path = tmp_path / "passport.txt"
    passport_path.write_text("  test-passport\n", encoding="utf-8")
    scope: NotebookScope = {}

    with (
        patch(
            "builtins.input",
            side_effect=["SRA", "SRR123456", str(passport_path), str(output_directory)],
        ),
        patch.object(logging, "basicConfig"),
    ):
        execute_notebook_cell(CONFIGURATION_CELL_ID, scope)

    config = cast(SimpleNamespace, scope["config"])
    assert config.source == "sra/SRR123456"
    assert config.output_directory == output_directory
    assert config.passport_text == "test-passport"
    assert config.idx_base_url == "https://locate-beta.ncbi.nlm.nih.gov/idx/v2"
    assert config.drs_base_url == "https://locate-beta.ncbi.nlm.nih.gov/ga4gh/drs/v1"
    assert output_directory.is_dir()
    output = capsys.readouterr().out
    assert_contains(passport_path, output)
    assert_contains(config.source, output)
    assert_contains(output_directory.resolve(), output)
    assert config.passport_text not in output


def test_manifest_request_uses_the_selected_source(capsys: pytest.CaptureFixture[str]) -> None:
    payload = {
        "response": {
            "contents": {
                "first-id": {"name": "first.txt"},
                "second-id": {"name": "second.txt"},
            }
        }
    }
    response = MagicMock(spec=requests.Response)
    response.json.return_value = payload
    config = SimpleNamespace(idx_base_url="https://idx.example.test/idx/v2", source="sra/SRR123456")
    scope: NotebookScope = {
        "config": config,
        "requests": requests,
    }

    with patch.object(requests, "get", return_value=response) as get:
        execute_notebook_cell(MANIFEST_REQUEST_CELL_ID, scope)

    get.assert_called_once_with(
        "https://idx.example.test/idx/v2/compound-object-manifest/sra/SRR123456",
        timeout=60,
    )
    response.raise_for_status.assert_called_once_with()
    response.json.assert_called_once_with()
    assert scope["resp"] is response
    assert scope["j"] is payload
    output = capsys.readouterr().out
    assert_contains(config.source, output)
    assert_matches(r"\b2\b", output)


def test_download_returns_after_drs_metadata_error(
    tmp_path: Path, caplog: pytest.LogCaptureFixture
) -> None:
    download = define_download_function()
    metadata_response = MagicMock(spec=requests.Response)
    metadata_response.raise_for_status.side_effect = requests.exceptions.HTTPError(
        "unavailable", response=metadata_response
    )
    destination = tmp_path / "file.txt"

    with (
        patch.object(requests, "get", return_value=metadata_response) as get,
        patch.object(requests, "post") as post,
        caplog.at_level(logging.ERROR),
    ):
        elapsed_seconds = download("drs-id", destination, 2, 5)

    get.assert_called_once_with(
        "https://drs.example.test/ga4gh/drs/v1/objects/drs-id",
        timeout=60,
    )
    post.assert_not_called()
    assert len(caplog.records) == 1
    assert caplog.records[0].levelno == logging.ERROR
    log_message = caplog.messages[0]
    assert_matches(r"\b2\b", log_message)
    assert_contains(destination, log_message)
    assert_contains("drs-id", log_message)
    assert elapsed_seconds is None
    assert not destination.exists()


def test_download_streams_the_first_successful_access_method(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    caplog: pytest.LogCaptureFixture,
) -> None:
    download = define_download_function()
    metadata_response = MagicMock(spec=requests.Response)
    metadata_response.json.return_value = {"access_methods": [{"access_id": "access-id"}]}
    access_response = MagicMock(spec=requests.Response)
    access_response.json.return_value = {"url": "https://download.example.test/file.txt"}
    file_response = MagicMock(spec=requests.Response)
    file_response.__enter__.return_value = file_response
    file_response.iter_content.return_value = [b"first", b"", b"second"]
    destination = tmp_path / "file.txt"

    with (
        patch.object(
            requests,
            "get",
            side_effect=[metadata_response, file_response],
        ) as get,
        patch.object(requests, "post", return_value=access_response) as post,
        caplog.at_level(logging.INFO),
    ):
        elapsed_seconds = download("drs-id", destination, 3, 7)

    assert get.call_args_list == [
        call("https://drs.example.test/ga4gh/drs/v1/objects/drs-id", timeout=60),
        call("https://download.example.test/file.txt", stream=True),
    ]
    post.assert_called_once_with(
        "https://drs.example.test/ga4gh/drs/v1/objects/drs-id/access/access-id",
        data=json.dumps({"passports": ["test-passport"]}),
        headers={"Content-type": "application/json"},
        timeout=60,
    )
    metadata_response.raise_for_status.assert_called_once_with()
    access_response.raise_for_status.assert_called_once_with()
    file_response.raise_for_status.assert_called_once_with()
    file_response.iter_content.assert_called_once_with(chunk_size=8192)
    log_messages = "\n".join(caplog.messages)
    assert_contains(destination, log_messages)
    assert_matches(r"\bdrs-id\b", log_messages)
    assert_contains(
        "https://drs.example.test/ga4gh/drs/v1/objects/drs-id/access/access-id",
        log_messages,
    )
    assert elapsed_seconds is not None
    assert elapsed_seconds >= 0
    assert destination.read_bytes() == b"first" b"second"
    output = capsys.readouterr().out
    assert_matches(r"\b3\b", output)
    assert_matches(r"\b7\b", output)
    assert_contains(destination.name, output)


def test_download_tries_the_next_access_method_after_an_error(
    tmp_path: Path, caplog: pytest.LogCaptureFixture
) -> None:
    download = define_download_function()
    metadata_response = MagicMock(spec=requests.Response)
    metadata_response.json.return_value = {
        "access_methods": [{"access_id": "unavailable"}, {"access_id": "working"}]
    }
    unavailable_response = MagicMock(spec=requests.Response)
    unavailable_response.raise_for_status.side_effect = requests.exceptions.HTTPError(
        "unavailable", response=unavailable_response
    )
    working_response = MagicMock(spec=requests.Response)
    working_response.json.return_value = {"url": "https://download.example.test/file.txt"}
    file_response = MagicMock(spec=requests.Response)
    file_response.__enter__.return_value = file_response
    file_response.iter_content.return_value = [b"contents"]
    destination = tmp_path / "file.txt"

    with (
        patch.object(requests, "get", side_effect=[metadata_response, file_response]),
        patch.object(
            requests,
            "post",
            side_effect=[unavailable_response, working_response],
        ) as post,
        caplog.at_level(logging.INFO),
    ):
        elapsed_seconds = download("drs-id", destination, 1, 1)

    assert [request.args[0] for request in post.call_args_list] == [
        "https://drs.example.test/ga4gh/drs/v1/objects/drs-id/access/unavailable",
        "https://drs.example.test/ga4gh/drs/v1/objects/drs-id/access/working",
    ]
    error_messages = [
        record.getMessage() for record in caplog.records if record.levelno >= logging.ERROR
    ]
    assert len(error_messages) == 1
    assert_contains(destination, error_messages[0])
    info_messages = "\n".join(
        record.getMessage() for record in caplog.records if record.levelno == logging.INFO
    )
    assert_contains(destination, info_messages)
    assert_matches(r"\bdrs-id\b", info_messages)
    assert elapsed_seconds is not None
    assert destination.read_bytes() == b"contents"


def test_download_logs_when_all_access_methods_fail(
    tmp_path: Path, caplog: pytest.LogCaptureFixture
) -> None:
    download = define_download_function()
    metadata_response = MagicMock(spec=requests.Response)
    metadata_response.json.return_value = {"access_methods": [{"access_id": "unavailable"}]}
    access_response = MagicMock(spec=requests.Response)
    access_response.raise_for_status.side_effect = requests.exceptions.HTTPError(
        "unavailable", response=access_response
    )
    destination = tmp_path / "file.txt"

    with (
        patch.object(requests, "get", return_value=metadata_response),
        patch.object(requests, "post", return_value=access_response),
        caplog.at_level(logging.INFO),
    ):
        elapsed_seconds = download("drs-id", destination, 4, 9)

    assert all(record.levelno >= logging.ERROR for record in caplog.records)
    assert len(caplog.messages) == 2
    assert_contains(destination, caplog.messages[0])
    final_message = caplog.messages[1]
    assert_matches(r"\b4\b", final_message)
    assert_matches(r"\bdrs-id\b", final_message)
    assert_contains(destination, final_message)
    assert elapsed_seconds is None
    assert not destination.exists()


def test_manifest_loop_downloads_each_drs_id_to_its_basename(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    download = MagicMock(side_effect=[1.25, 2.5])
    scope: NotebookScope = {
        "Path": Path,
        "config": SimpleNamespace(output_directory=tmp_path),
        "datetime": datetime,
        "dl_drs_id_to_file": download,
        "j": {
            "response": {
                "contents": {
                    "first-id": {"name": "first/path/shared.txt"},
                    "second-id": {"name": "second/path/shared.txt"},
                }
            }
        },
        "time": MagicMock(),
    }

    execute_notebook_cell(DOWNLOAD_LOOP_CELL_ID, scope)

    assert download.call_args_list == [
        call("first-id", tmp_path / "shared.txt", 1, 2),
        call("second-id", tmp_path / "shared.txt", 2, 2),
    ]
    assert scope["download_times"] == [1.25, 2.5]
    assert scope["download_failures"] == 0
    output = capsys.readouterr().out
    assert_matches(r"\b2\b", output)
    assert_contains(tmp_path.resolve(), output)


def test_manifest_loop_retries_then_reports_a_failed_download(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    download = MagicMock(return_value=None)
    time_module = MagicMock()
    scope: NotebookScope = {
        "Path": Path,
        "config": SimpleNamespace(output_directory=tmp_path),
        "datetime": datetime,
        "dl_drs_id_to_file": download,
        "j": {
            "response": {
                "contents": {
                    "failed-id": {"name": "some/path/failed.txt"},
                }
            }
        },
        "time": time_module,
    }

    execute_notebook_cell(DOWNLOAD_LOOP_CELL_ID, scope)

    assert download.call_args_list == [
        call("failed-id", tmp_path / "failed.txt", 1, 1),
        call("failed-id", tmp_path / "failed.txt", 1, 1),
        call("failed-id", tmp_path / "failed.txt", 1, 1),
        call("failed-id", tmp_path / "failed.txt", 1, 1),
    ]
    assert time_module.sleep.call_args_list == [call(15), call(15), call(15)]
    assert scope["download_times"] == []
    assert scope["download_failures"] == 1
    output = capsys.readouterr().out
    assert_contains("failed.txt", output)
    assert_matches(r"\b4\b", output)
