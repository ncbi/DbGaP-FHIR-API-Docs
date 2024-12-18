import json
from unittest.mock import patch, MagicMock
from pilot.jupyter.fhir_fetcher import fetch_all_data


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
    mock_response1 = mock_response_with_entries([
                        {"resource": {"id": "1"}}],
                "http://example.com/next")
    mock_response2 = mock_response_with_entries([{"resource": {"id": "2"}}])
    mock_session.get.side_effect = [mock_response1, mock_response2]

    result = fetch_all_data(mock_session, "http://example.com", num_pages=1)

    assert len(result) == 1
    assert result[0]["resource"]["id"] == "1"
