from unittest.mock import patch, MagicMock
import pandas as pd
from pandas.testing import assert_frame_equal
from jupyter.dbgap_fhir import DbGapFHIR, obs_to_df

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

@patch('os.path.expanduser')
@patch('builtins.open', new_callable=MagicMock)
@patch('requests.Session')
def test_add_passport_with_file(MockSession, mock_open, mock_expanduser):
    # Setup mocks
    mock_session = MockSession.return_value
    # Make headers a MagicMock instead of a regular dictionary
    mock_session.headers = MagicMock()
    mock_response = MagicMock()
    mock_session.get.return_value = mock_response

    # Set up file reading mock
    mock_file = MagicMock()
    mock_file.read.return_value = "test_passport_token"
    mock_open.return_value.__enter__.return_value = mock_file

    # Set up path expansion
    mock_expanduser.return_value = "/expanded/path/to/passport.txt"

    # Create client with passport
    client = DbGapFHIR(fhir_server="http://example.com", passport="~/passport.txt")

    # Verify the passport file was read correctly
    mock_expanduser.assert_called_once_with("~/passport.txt")
    mock_open.assert_called_once_with("/expanded/path/to/passport.txt")

    mock_session.headers.update.assert_called_with({"Authorization": "Bearer "
                                                              "test_passport_token"})
    mock_session.headers.update.assert_called_with({"Authorization": "Bearer "
                                                    "test_passport_token"})


def test_obs_to_df():
    # Create test observations with different value types and naming scenarios
    observations = [
        # Observation with valueQuantity
        {
            "subject": {"reference": "Patient/123"},
            "code": {"coding": [{"display": "Height", "code": "8302-2"}]},
            "valueQuantity": {"value": 175.2, "unit": "cm"}
        },
        # Observation with valueCodeableConcept
        {
            "subject": {"reference": "Patient/123"},
            "code": {"coding": [{"display": "Gender", "code": "263495000"}]},
            "valueCodeableConcept": {"coding": [{"display": "Male"}]}
        },
        # Observation without a specific value
        {
            "subject": {"reference": "Patient/123"},
            "code": {"coding": [{"display": "Observation", "code": "1234"}]}
        },
        # Special naming case for SUBJECT_ID
        {
            "subject": {"reference": "Patient/456"},
            "code": {"coding": [{"display": "SUBJECT_ID", "code": "SUB001"}]},
            "valueQuantity": {"value": "S12345", "unit": ""}
        },
        # Special naming case for SAMPLE_ID
        {
            "subject": {"reference": "Patient/456"},
            "code": {"coding": [{"display": "SAMPLE_ID", "code": "SAM001"}]},
            "valueQuantity": {"value": "B789", "unit": ""}
        }
    ]

    # Call the function
    result_df = obs_to_df(observations)

    # Create the expected DataFrame
    expected_data = {
        "Patient/123": {
            "Height": 175.2,
            "Gender": "Male",
            "Observation": "unknown"
        },
        "Patient/456": {
            "SUBJECT_ID_SUB001": "S12345",
            "SAMPLE_ID_SAM001": "B789"
        }
    }
    expected_df = pd.DataFrame.from_dict(expected_data, orient="index")

    # Compare the DataFrames
    assert_frame_equal(result_df, expected_df, check_like=True)

    # Basic validations
    assert len(result_df) == 2  # Two unique subjects
    assert "Height" in result_df.columns
    assert "SUBJECT_ID_SUB001" in result_df.columns
    assert result_df.loc["Patient/123", "Gender"] == "Male"
    assert result_df.loc["Patient/456", "SAMPLE_ID_SAM001"] == "B789"