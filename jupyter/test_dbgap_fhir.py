from unittest.mock import patch, MagicMock
from jupyter.dbgap_fhir import DbGapFHIR


@patch('requests.Session')
def test_run_query_with_limit(MockSession):
    mock_session = MockSession.return_value
    mock_response = MagicMock()
    mock_response.json.return_value = {"entry": [{"resource": {"id": "1"}}]}
    mock_response.content = b'{"entry": [{"resource": {"id": "1"}}]}'
    mock_session.get.return_value = mock_response

    client = DbGapFHIR(fhir_server="http://example.com")
    result = client.run_query("Patient", limit=True)

    assert len(result) == 1
    assert result[0]["id"] == "1"


@patch('requests.Session')
def test_resolve_pages(MockSession):
    mock_session = MockSession.return_value
    mock_response_metadata = MagicMock()
    mock_response_page_1 = MagicMock()
    mock_response_page_2 = MagicMock()

    mock_response_metadata.json.return_value = {
        "metadata": "data",
    }

    # Mock the first page response
    mock_response_page_1.json.return_value = {
        "link": [{"relation": "next", "url": "http://example.com/page2"}],
        "entry": [{"resource": {"id": "1"}}]
    }

    # Mock the second page response
    mock_response_page_2.json.return_value = {
        "entry": [{"resource": {"id": "2"}}]
    }

    # Set the return values for the session's get method
    mock_session.get.side_effect = [mock_response_metadata,
                                    mock_response_page_1,
                                    mock_response_page_2]

    client = DbGapFHIR(fhir_server="http://example.com")
    bundle = {
        "link": [{"relation": "next", "url": "http://example.com/page1"}],
        "entry": [{"resource": {"id": "0"}}]
    }

    result = client.resolve_pages(bundle)

    assert len(result) == 2
    assert result[0]["entry"][0]["resource"]["id"] == "0"
    assert result[1]["entry"][0]["resource"]["id"] == "1"