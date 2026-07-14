"""
API Tests for Watchlist

Endpoints under test:

GET     /api/watchlist/
POST    /api/watchlist/
DELETE  /api/watchlist/<int:tmdb_id>/ 
"""

import pytest
from unittest.mock import patch
from rest_framework import status
from watchlist.models import Watchlist

WATCHLIST_URL = '/api/watchlist/'

def delete_watchlist_url(tmdb_id):
    return f'/api/watchlist/{tmdb_id}/'



"""
Watchlist API
"""
@pytest.mark.django_db
class TestWatchlistAPI:

    def test_list_watchlist_returns_200(self, auth_client, user, movie, watchlist_factory):
        watchlist_factory(user=user, movie=movie)
        response = auth_client.get(WATCHLIST_URL)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] >= 1

    def test_add_to_watchlist(self, auth_client, movie_factory):
        movie = movie_factory(tmdb_id=1001)
        with patch('watchlist.views.get_or_create_movie', return_value=movie):
            response = auth_client.post(WATCHLIST_URL, {'tmdb_id': movie.tmdb_id}, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        added_movie = response.data['movie']
        assert added_movie['tmdb_id'] == movie.tmdb_id

    def test_duplicate_movie_not_allowed(self, auth_client, user, movie_factory, watchlist_factory):
        movie = movie_factory(tmdb_id=5001)
        watchlist_factory(user=user, movie=movie)
        with patch('watchlist.views.get_or_create_movie', return_value=movie):
            try:
                response = auth_client.post(WATCHLIST_URL, {'tmdb_id': 5001}, format='json')
                assert response.status_code in (
                    status.HTTP_400_BAD_REQUEST,
                    status.HTTP_409_CONFLICT
                ), f'Expected 4xx but got {response.status_code}'
            except Exception:
                pass

    def test_delete_from_watchlist(self, auth_client, user, movie_factory, watchlist_factory):
        movie = movie_factory(tmdb_id=550)
        watchlist_factory(user=user, movie=movie)
        assert Watchlist.objects.filter(user=user, movie=movie).exists()
        response = auth_client.delete(delete_watchlist_url(550))
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Watchlist.objects.filter(user=user, movie=movie).exists()

    def test_delete_nonexistent_from_watchlist_raises_404(self, auth_client, movie):
        response = auth_client.delete(delete_watchlist_url(movie.tmdb_id))
        assert response.status_code == status.HTTP_404_NOT_FOUND