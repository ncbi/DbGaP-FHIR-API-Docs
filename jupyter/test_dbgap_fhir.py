from unittest.mock import patch, MagicMock
from jupyter.dbgap_fhir import DbGapFHIR, obs_to_df, prettyprint



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