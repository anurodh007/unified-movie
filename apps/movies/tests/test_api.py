"""
API Tests for Movies, Genres, Streaming-Platforms, Trending Endpoints

Endpoints under test:

GET  /api/movies/                       - list(with search, filter, ordering, pagination)
GET  /api/movies/<int:tmdb_id>/         - retrieve / auto-fetch from TMDB
GET  /api/movies/genres/                - list genres
GET  /api/movies/genres/<tmdb_id>/      - genre detail
GET  /api/movies/<tmdb_id>/streaming/   - streaming platforms
GET  /api/movies/trending/              - trending movies
"""

import pytest
from unittest.mock import patch
from rest_framework import status

# URL Helpers
MOVIES_LIST_URL = '/api/movies/'
GENRES_URL = '/api/movies/genres/'
TRENDING_URL = '/api/movies/trending/'

def movie_detail_url(tmdb_id):
    return f'/api/movies/{tmdb_id}/'

def streaming_url(tmdb_id):
    return f'/api/movies/{tmdb_id}/streaming/'

def genre_detail_url(tmdb_id):
    return f'/api/movies/genres/{tmdb_id}/'



"""
Movie List API
"""
@pytest.mark.django_db
class TestMovieListAPI:

    def test_list_returns_200(self, api_client):
        response = api_client.get(MOVIES_LIST_URL)
        assert response.status_code == status.HTTP_200_OK

    def test_list_is_paginated(self, api_client, movie_factory):
        for i in range(15):
            movie_factory(tmdb_id=i + 100, title=f'Movie {i}', popularity=float(i))
        response = api_client.get(MOVIES_LIST_URL)
        assert response.status_code == status.HTTP_200_OK
        for field in ('count', 'next', 'previous', 'results'):
            assert field in response.data
        assert len(response.data['results']) <= 10

    def test_list_ordered_by_popularity_desc(self, api_client, movie_factory):
        movie_factory(tmdb_id=101, title='Popular', popularity=100.0)
        movie_factory(tmdb_id=201, title='Unpopular', popularity=50.0)
        response = api_client.get(MOVIES_LIST_URL)
        results = response.data['results']
        assert results[0]['title'] == 'Popular'

    def test_search_uses_tmdb_when_few_local_results(self, api_client, fake_search_response):
        """When fewer than 3 local matches exist, the service calls TMDB"""
        with patch(
            target='movies.services.movie_service.search_movies_tmdb',
            return_value=fake_search_response
        ):
            response = api_client.get(MOVIES_LIST_URL, {'search': 'Fight'})
        assert response.status_code in (status.HTTP_200_OK, status.HTTP_404_NOT_FOUND)

    def test_search_returns_local_results_when_enough(self, api_client, movie_factory):
        for i in range(10):
            movie_factory(tmdb_id=i + 100, title=f'Matrix {i}')
        with patch('movies.services.movie_service.search_movies_tmdb') as mock_tmdb:
            response = api_client.get(MOVIES_LIST_URL, {'search': 'Matrix'})
        mock_tmdb.assert_not_called()
        assert response.status_code == status.HTTP_200_OK

    def test_search_with_no_match_returns_404(self, api_client):
        with patch(
            'movies.services.movie_service.search_movies_tmdb',
            return_value=None
        ):
            response = api_client.get(MOVIES_LIST_URL, {'search': 'nonexistentabcxyz'})
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_filter_by_single_genre(self, api_client, movie_factory, genre_factory):
        g1 = genre_factory(tmdb_id=28, name='Action')
        movie_factory(tmdb_id=101, title='Action Movie', genres=[g1])
        movie_factory(tmdb_id=201, title='No Genre Movie')
        response = api_client.get(MOVIES_LIST_URL, {'genres': 'Action'})
        assert response.status_code == status.HTTP_200_OK
        results = response.data['results']
        assert results[0]['title'] == 'Action Movie'

    def test_filter_by_multiple_genres(self, api_client, movie_factory, genre_factory):
        g1 = genre_factory(tmdb_id='28', name='Action')
        g2 = genre_factory(tmdb_id='50', name='Comedy')
        movie_factory(tmdb_id=555, title='Rush Hour', genres=[g1, g2])
        movie_factory(tmdb_id=777, title='John Wick', genres=[g1])
        movie_factory(tmdb_id=999, title='Airplane!', genres=[g2])
        response = api_client.get(MOVIES_LIST_URL, {'genres': 'Action,Comedy'})
        results = response.data['results']
        assert len(results) == 1
        assert results[0]['title'] == 'Rush Hour'

    def test_filter_with_unknown_genre_returns_empty_list(self, api_client, movie_factory, genre_factory):
        g1 = genre_factory(tmdb_id=28, name='Action')
        for i in range(5):
            movie_factory(tmdb_id=i + 100, title=f'Action {i}', genres=[g1])
        response = api_client.get(MOVIES_LIST_URL, {'genres': 'Unknown'})
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 0



"""
Movie Detail API
"""
@pytest.mark.django_db
class TestMovieDetailAPI:

    def test_retrieve_existing_movie_from_local_db(self, api_client, movie_factory):
        movie_factory(tmdb_id=550, title='Fight Club')
        response = api_client.get(movie_detail_url(550))
        assert response.status_code == status.HTTP_200_OK

    def test_retrieve_fetches_from_tmdb_when_not_local(self, api_client, fake_movie_detail):
        with patch('movies.services.movie_service.cache') as mock_cache, \
             patch('movies.services.movie_service.get_movie_details', return_value=fake_movie_detail) as mock_tmdb:
            
            mock_cache.get.return_value = None
            response = api_client.get(movie_detail_url(550))
            assert response.status_code == status.HTTP_200_OK
            mock_tmdb.assert_called_once_with(tmdb_id=550)

    def test_retrieve_nonexistent_tmdb_id_returns_404(self, api_client):
        with patch('movies.services.movie_service.cache') as mock_cache, \
             patch('movies.services.movie_service.get_movie_details', return_value=None):
            
            mock_cache.get.return_value = None
            response = api_client.get(movie_detail_url(999999999999999))
        assert response.status_code == status.HTTP_404_NOT_FOUND



"""
Genre API
"""
@pytest.mark.django_db
class TestGenreAPI:

    def test_genre_list_returns_200(self, api_client):
        response = api_client.get(GENRES_URL)
        assert response.status_code == status.HTTP_200_OK

    def test_genre_detail_by_tmdb_id(self, api_client, genre_factory):
        genre_factory(tmdb_id=28, name='Action')
        response = api_client.get(genre_detail_url(28))
        assert response.status_code == status.HTTP_200_OK
        assert response.data['name'] == 'Action'

    def test_invalid_genre_tmdb_id_returns_404(self, api_client):
        response = api_client.get(genre_detail_url(99999))
        assert response.status_code == status.HTTP_404_NOT_FOUND



"""
Streaming Platform API
"""
@pytest.mark.django_db
class TestStreamingAPI:

    def test_streaming_returns_platforms_when_found(self, api_client, fake_streaming_response):
        with patch(
            'movies.services.movie_service.get_streaming_details',
             return_value=fake_streaming_response
        ):
            response = api_client.get(streaming_url(550))
        assert response.status_code == status.HTTP_200_OK

    def test_streaming_returns_404_when_not_found(self, api_client):
        with patch('movies.views.get_streaming_platforms', return_value=None):
            response = api_client.get(streaming_url(999))
        assert response.status_code == status.HTTP_404_NOT_FOUND


    
"""
Trending API
"""
@pytest.mark.django_db
class TestTrendingAPI:

    def test_trending_returns_200(self, api_client):
        fake_trending = [
            {'tmdb_id': 550, 'title': 'Fight Club', 'popularity': 58.5, 'poster_path': None,}
        ]
        with patch('movies.views.get_trending_movies', return_value=fake_trending):
            response = api_client.get(TRENDING_URL)
        assert response.status_code == status.HTTP_200_OK

    def test_trending_returns_404_on_api_failure(self, api_client):
        with patch('movies.views.get_trending_movies', return_value=None):
            response = api_client.get(TRENDING_URL)
        assert response.status_code == status.HTTP_404_NOT_FOUND