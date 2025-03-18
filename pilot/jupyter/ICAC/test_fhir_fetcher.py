import json
import requests
from unittest.mock import patch, MagicMock
from fhir_fetcher import fetch_all_data


def mock_response_with_entries(entries, next_url=None):
    response = MagicMock()
    response.json.return_value = {
        "entry": entries,
        "link": [{"relation": "next", "url": next_url}] if next_url else []
    }
    response.content = json.dumps(response.json.return_value).encode('utf-8')
    return response


@patch('requests.Session')
def test_fetch_all_data_with_valid_response(MockSession):
    mock_session = MockSession.return_value
    mock_response1 = mock_response_with_entries([
        {"resource": {"id": "1"}}], "http://example.com/next")
    mock_response2 = mock_response_with_entries([{"resource": {"id": "2"}}])
    mock_session.get.side_effect = [mock_response1, mock_response2]

    result = fetch_all_data(mock_session, "http://example.com")

    assert len(result) == 2
    assert result[0]["resource"]["id"] == "1"
    assert result[1]["resource"]["id"] == "2"


@patch('requests.Session')
def test_fetch_all_data_with_no_entries(MockSession):
    mock_session = MockSession.return_value
    mock_response = mock_response_with_entries([])
    mock_session.get.return_value = mock_response

    result = fetch_all_data(mock_session, "http://example.com")

    assert len(result) == 0


@patch('requests.Session')
def test_fetch_all_data_with_other_error(MockSession):
    mock_session = MockSession.return_value
    mock_session.get.side_effect = Exception("Other Error")

    result = fetch_all_data(mock_session, "http://example.com")

    assert len(result) == 0


@patch('requests.Session')
def test_fetch_all_data_with_num_pages(MockSession):
    mock_session = MockSession.return_value
    mock_response1 = mock_response_with_entries(
        [{"resource": {"id": "1"}}],
        "http://example.com/next")
    mock_response2 = mock_response_with_entries([{"resource": {"id": "2"}}])
    mock_session.get.side_effect = [mock_response1, mock_response2]

    result = fetch_all_data(mock_session, "http://example.com", num_pages=1)

    assert len(result) == 1
    assert result[0]["resource"]["id"] == "1"


@patch('builtins.print')
@patch('requests.Session')
def test_fetch_all_data_with_print_entry(MockSession, mock_print):
    # Set up mock session
    mock_session = MockSession.return_value
    entries = [{"resource": {"id": "1"}}, {"resource": {"id": "2"}}]
    mock_response = mock_response_with_entries(entries)
    mock_session.get.return_value = mock_response

    # Call fetch_all_data with print_entry='y'
    result = fetch_all_data(mock_session, "http://example.com", print_entry='y')

    # Verify print function was called with expected arguments
    mock_print.assert_any_call("Data returned in this iteration:")

    # Verify that each entry was printed (using json.dumps)
    for entry in entries:
        entry_json = json.dumps(entry, indent=4)
        printed = False
        for call_args in mock_print.call_args_list:
            if call_args[0][0] == entry_json:
                printed = True
                break
        assert printed, f"Entry {entry} was not printed properly"

    # Verify the result contains expected entries
    assert len(result) == 2
    assert result[0]["resource"]["id"] == "1"
    assert result[1]["resource"]["id"] == "2"


@patch('builtins.print')
@patch('requests.Session')
def test_fetch_all_data_with_http_error_and_value_error(MockSession, mock_print):
    # Set up mock session and response
    mock_session = MockSession.return_value
    mock_response = MagicMock()
    mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("404 Client Error")
    mock_response.json.side_effect = ValueError("Invalid JSON")
    mock_response.content = b"Not a JSON response"
    mock_session.get.return_value = mock_response

    # Call the function under test
    result = fetch_all_data(mock_session, "http://example.com")

    # Verify the result is empty (due to the error)
    assert len(result) == 0

    # Verify that the appropriate error messages were printed
    mock_print.assert_any_call("HTTP error occurred: 404 Client Error")
    mock_print.assert_any_call("Response content: b'Not a JSON response'")