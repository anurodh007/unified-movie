"""
Tests for movies/services/movie_service.py 

Every util mocks tmdb_client
"""

import pytest
from unittest.mock import patch

from movies.models import StreamingPlatform
from movies.services.movie_service import (
    get_or_create_movie,
    search_movies,
    get_streaming_platforms,
)

TARGET_CACHE_STRING = 'movies.services.movie_service.cache'



"""
get_or_create_movie
"""
@pytest.mark.django_db
class TestGetOrCreateMovieUtil:

    TARGET_STRING = 'movies.services.movie_service.get_movie_details'

    def test_returns_existing_movie_from_db(self, movie_factory):
        movie_factory(tmdb_id=5001, title='Local Movie')
        with patch(TARGET_CACHE_STRING) as mock_cache:
            mock_cache.get.return_value = None
            with patch(self.TARGET_STRING) as mock_tmdb:
                movie = get_or_create_movie(5001)
        mock_tmdb.assert_not_called()
        assert movie.tmdb_id == 5001

    def test_creates_movie_from_tmdb(self, db, fake_movie_detail):
        with patch(TARGET_CACHE_STRING) as mock_cache, \
             patch(self.TARGET_STRING, return_value=fake_movie_detail) as mock_tmdb:
            mock_cache.get.return_value = None
            movie = get_or_create_movie(5001)
        mock_tmdb.assert_called()
        assert movie is not None
        assert movie.tmdb_id == 550
        genres = set(movie.genres.values_list('name', flat=True))
        assert 'Drama' in genres
        assert 'Thriller' in genres



"""
search_movies
"""
@pytest.mark.django_db
class TestSearchMoviesUtil:

    TARGET_STRING = 'movies.services.movie_service.search_movies_tmdb'

    def test_returns_results_from_db_when_enough(self, movie_factory):
        """Returns list from local db when more than 3 matches"""
        for i in range(15):
            movie_factory(tmdb_id=i + 100, title=f'Matrix {i}')
        with patch(TARGET_CACHE_STRING) as mock_cache, \
             patch(self.TARGET_STRING) as mock_tmdb:
            mock_cache.get.return_value = None
            result = search_movies('Matrix')
        mock_tmdb.assert_not_called()
        assert result is not None
        assert result[0].tmdb_id == 100

    def test_strips_whitespace_from_query(self, db):
        with patch(TARGET_CACHE_STRING) as mock_cache, \
             patch(self.TARGET_STRING) as mock_tmdb:
            mock_cache.get.return_value = None
            mock_tmdb.return_value = None
            result = search_movies('   ')
        assert result is None



"""
get_streaming_platforms
"""
@pytest.mark.django_db
class TestGetStreamingPlatformsUtil:

    TARGET_STRING = 'movies.services.movie_service.get_streaming_details'

    def test_returns_us_providers(self, db, fake_streaming_response):
        StreamingPlatform.objects.create(tmdb_id=8, name='Netflix')
        with patch(TARGET_CACHE_STRING) as mock_cache, \
             patch(self.TARGET_STRING, return_value=fake_streaming_response):
            mock_cache.get.return_value = None
            result = get_streaming_platforms(550)
        provider_ids = set(result.values_list('tmdb_id', flat=True))
        assert 8 in provider_ids

    def test_returns_none_when_api_fails(self):
        with patch(TARGET_CACHE_STRING) as mock_cache, \
             patch(self.TARGET_STRING, return_value=None):
            mock_cache.get.return_value = None
            result = get_streaming_platforms(-1)
        assert result is None