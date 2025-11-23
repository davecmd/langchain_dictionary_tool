import pytest
from unittest.mock import patch
from merriam_webster_tool import MerriamWebster
import requests
import os

MW_API_KEY = os.getenv("MW_API_KEY")


if MW_API_KEY is None:
    raise ValueError("API_KEY environment variable is not set.")

def test_run_empty_word():
    ''' Returns a prompt message when input is empty. '''

    tool = MerriamWebster(api_key="fakekey")
    result = tool._run("")
    assert result == "Please provide a word to look up."

def test_valid_word():
    ''' Formats a valid definition correctly from a mock response. '''

    tool = MerriamWebster(api_key="dummy_key")
    result = tool._format_api_response("test", [{"shortdef": ["a procedure"], "fl": "noun", "hwi": {"hw": "test"}}])
    assert "Definition of 'test'" in result

@patch("requests.get")
def test_run_no_results(mock_get):
    ''' Handles API response with no results correctly. '''

    mock_get.return_value.json.return_value = []
    mock_get.return_value.raise_for_status = lambda: None

    tool = MerriamWebster(api_key="fakekey")
    result = tool._run("asdfghjkl")
    assert result == "No results found for 'asdfghjkl'."


@patch("requests.get")
def test_run_suggestions(mock_get):
    ''' Returns spelling suggestions when API provides alternatives. '''

    mock_get.return_value.json.return_value = ["cat", "bat", "rat"]
    mock_get.return_value.raise_for_status = lambda: None

    tool = MerriamWebster(api_key="fakekey")
    result = tool._run("cta")
    assert "You can try one of the following alternatives" in result


@patch("requests.get")
def test_run_definition(mock_get):
    ''' Formats a single definition correctly from a mock API response. '''

    mock_get.return_value.json.return_value = [
        {
            "meta": {"id": "cat:1"},
            "hwi": {"hw": "cat"},
            "fl": "noun",
            "shortdef": ["a small domesticated carnivorous mammal"]
        }
    ]
    mock_get.return_value.raise_for_status = lambda: None

    tool = MerriamWebster(api_key="fakekey")
    result = tool._run("cat")
    assert "Definition of 'cat'" in result
    assert "cat, noun, a small domesticated carnivorous mammal" in result


@patch("requests.get")
def test_run_multiple_definitions(mock_get):
    ''' Formats multiple short definitions correctly and numbers them. '''

    mock_get.return_value.json.return_value = [
        {
            "meta": {"id": "run:1"},
            "hwi": {"hw": "run"},
            "fl": "verb",
            "shortdef": ["move swiftly", "operate"]
        }
    ]
    mock_get.return_value.raise_for_status = lambda: None

    tool = MerriamWebster(api_key="fakekey")
    result = tool._run("run")
    assert "Definitions of 'run'" in result
    assert "1. run, verb, move swiftly" in result
    assert "2. run, verb, operate" in result


def test_format_definition_no_hwi():
    ''' Handles definitions that lack 'hwi' key, using meta ID instead. '''

    tool = MerriamWebster(api_key="fakekey")
    definition = {
        "meta": {"id": "foobar:1"},
        "fl": "noun",
        "shortdef": ["a placeholder"]
    }
    formatted = list(tool._format_definition(definition))
    assert formatted[0] == "foobar, noun, a placeholder"


@patch("requests.get")
def test_run_strip_input(mock_get):
    ''' Strips whitespace from input before querying the API. '''

    mock_get.return_value.json.return_value = [
        {
            "meta": {"id": "hello:1"},
            "hwi": {"hw": "hello"},
            "fl": "interjection",
            "shortdef": ["used as a greeting"]
        }
    ]
    mock_get.return_value.raise_for_status = lambda: None

    tool = MerriamWebster(api_key="fakekey")
    result = tool._run("   hello  ")
    assert "hello" in result
    assert "interjection" in result


# Integration tests (require a valid API key)
@pytest.mark.integration
def test_integration_real_word():
    ''' Retrieves real definition for a valid word. '''

    tool = MerriamWebster(api_key=MW_API_KEY)
    result = tool._run("computer")
    assert "computer" in result.lower()


@pytest.mark.integration
def test_integration_nonexistent_word():
    ''' Returns 'No results' or suggestions for a nonexistent word. '''

    tool = MerriamWebster(api_key=MW_API_KEY)
    result = tool._run("asdasdasdasdl")
    assert "No results found" in result or "Did you mean" in result


# HTTP error handling test
@patch("requests.get")
def test_http_error(mock_get):
    ''' Raises HTTPError when the API request fails. '''
    def raise_http_error():
        raise requests.exceptions.HTTPError("401 Unauthorized")
    mock_get.return_value.raise_for_status = raise_http_error

    tool = MerriamWebster(api_key="fakekey")
    with pytest.raises(requests.exceptions.HTTPError):
        tool._run("cat")
