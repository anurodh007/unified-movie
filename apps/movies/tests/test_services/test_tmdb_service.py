"""
Unit Tests for movies/services/tmdb_client.py

Every test mocks 'requests.get' so that no real HTTP traffic occurs.
"""

import pytest
from unittest.mock import patch, MagicMock
from requests.exceptions import ConnectionError, Timeout, HTTPError

from movies.services.tmdb_client import (
    BASE_URL,
    get_movie_details,
    search_movies_tmdb,
    get_streaming_details,
    get_trending_movies_by_day
)

TARGET_ENDPOINT = 'movies.services.tmdb_client.requests.get'


# Helper to build a minimal mock response
def _mock_response(json_data=None, status_code=200, raise_for_status=None):
    mock = MagicMock()
    mock.status_code = status_code
    mock.json.return_value = json_data or {}
    if raise_for_status:
        mock.raise_for_status.side_effect = raise_for_status
    else:
        mock.raise_for_status.return_value = None
    return mock



"""
get_movie_details
"""
class TestGetMovieDetails:

    def test_returns_json_on_success(self):
        fake = {'tmdb_id': 550, 'title': 'Fight Club'}
        with patch(TARGET_ENDPOINT) as mock_get:
            mock_get.return_value = _mock_response(json_data=fake)
            result = get_movie_details(550)
        assert result == fake

    def test_returns_none_on_connection_error(self):
        with patch(TARGET_ENDPOINT, side_effect=ConnectionError()):
            result = get_movie_details(550)
        assert result is None

    def test_returns_none_on_timeout(self):
        with patch(TARGET_ENDPOINT, side_effect=Timeout()):
            result = get_movie_details(550)
        assert result is None

    def test_returns_none_on_http_error(self):
        with patch(TARGET_ENDPOINT) as mock_get:
            mock_get.return_value = _mock_response(status_code=401, raise_for_status=HTTPError('Invalid API Key'))
            result = get_movie_details(550)
        assert result is None

    def test_returns_none_if_invalid_tmdb_id(self):
        with patch(TARGET_ENDPOINT) as mock_get:
            mock_get.return_value = _mock_response(status_code=404, raise_for_status=HTTPError('Not Found'))
            result = get_movie_details(-1)
        assert result is None

    def test_calls_correct_endpoint(self):
        with patch(TARGET_ENDPOINT) as mock_get:
            mock_get.return_value = _mock_response(json_data={'id': 550})
            get_movie_details(550)
        call_url = mock_get.call_args[0][0]
        assert call_url == f'{BASE_URL}/movie/550'



"""
search_movies_tmdb
"""
class TestSearchMoviesTMDB:

    def test_returns_results_on_success(self):
        fake = {'results': [{'id': 550, 'title': 'Fight Club'}]}
        with patch(TARGET_ENDPOINT) as mock_get:
            mock_get.return_value = _mock_response(json_data=fake)
            result = search_movies_tmdb('fight')
        assert result['results'][0]['title'] == 'Fight Club'

    def test_returns_none_on_request_exception(self):
        with patch(TARGET_ENDPOINT, side_effect=Timeout()):
            result = search_movies_tmdb('any')
        assert result is None

    def test_empty_query_still_calls_api(self):
        with patch(TARGET_ENDPOINT) as mock_get:
            mock_get.return_value = _mock_response({'results': [{}]})
            result = search_movies_tmdb('')
        mock_get.assert_called()

    def test_api_failure_returns_none(self):
        with patch(TARGET_ENDPOINT) as mock_get:
            mock_get.return_value = _mock_response(status_code=500, raise_for_status=HTTPError('Server Error'))
            result = search_movies_tmdb('error')
        assert result is None



"""
get_streaming_details
"""
class TestGetStreamingDetails:

    def test_returns_providers_on_success(self):
        fake = {'results': {'US': {'flatrate': [{'provider_id': 8, 'provider_name': 'Netflix'}]}}}
        with patch(TARGET_ENDPOINT) as mock_get:
            mock_get.return_value = _mock_response(json_data=fake)
            result = get_streaming_details(550)
        assert result == fake

    def test_returns_none_on_failure(self):
        with patch(TARGET_ENDPOINT, side_effect=ConnectionError()):
            result = get_streaming_details(550)
        assert result is None



"""
get_trending_movies_by_day
"""
class TestGetTrendingMoviesByDay:

    def test_returns_results_on_success(self):
        fake = {'results': [{'id': 550, 'title': 'Fight Club'}, {'id': 19542, 'title': 'The Red Shoes'}]}
        with patch(TARGET_ENDPOINT) as mock_get:
            mock_get.return_value = _mock_response(json_data=fake)
            result = get_trending_movies_by_day()
        assert result == fake

    def test_returns_none_on_failue(self):
        with patch(TARGET_ENDPOINT) as mock_get:
            mock_get.return_value = _mock_response(status_code=401, raise_for_status=HTTPError('Incorrect API Key'))
            result = get_trending_movies_by_day()
        assert result is None

    def test_calls_trending_endpoint(self):
        with patch(TARGET_ENDPOINT) as mock_get:
            mock_get.return_value = _mock_response(json_data={'results': []})
            result = get_trending_movies_by_day()
        call_url = mock_get.call_args[0][0]
        assert call_url == f'{BASE_URL}/trending/movie/day'