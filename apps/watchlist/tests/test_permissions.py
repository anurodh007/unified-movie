"""
Tests Watchlist permissions

Endpoints under test:

GET /api/users/<str:username>/watchlist/

GET /api/watchlist/
POST /api/watchlist/
DELETE /api/watchlist/<int:tmdb_id>/
"""

import pytest
from django.urls import reverse
from rest_framework import status
from watchlist.models import Watchlist



"""
Watchlist Permission Tests
"""
@pytest.mark.django_db
class TestWatchlistPermission:

    def test_anonymous_user_can_view_users_watchlist(self, api_client, user):
        url = reverse('user-watchlist-list', kwargs={'username': user.username})
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK

    def test_anonymous_user_cannot_view_own_watchlist(self, api_client):
        url = reverse('user-watchlist')
        response = api_client.get(url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_anonymous_user_cannot_add_movie_to_watchlist(self, api_client, movie):
        response = api_client.post(reverse('user-watchlist'), {'tmdb_id': movie.tmdb_id}, format='json')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_anonymous_user_cannot_delete_movie_from_watchlist(self, api_client, movie):
        url = reverse('user-watchlist-delete', kwargs={'tmdb_id': movie.tmdb_id})
        response = api_client.delete(url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_authenticated_user_can_view_own_watchlist(self, auth_client):
        url = reverse('user-watchlist')
        response = auth_client.get(url)
        assert response.status_code == status.HTTP_200_OK

    def test_user_can_add_movie_to_own_watchlist(self, auth_client, movie):
        response = auth_client.post(reverse('user-watchlist'), {'tmdb_id': movie.tmdb_id}, format='json')
        assert response.status_code == status.HTTP_201_CREATED

    def test_user_can_delete_movie_from_their_watchlist(self, auth_client, user, movie):
        wl = Watchlist.objects.create(user=user, movie=movie)
        url = reverse('user-watchlist-delete', kwargs={'tmdb_id': wl.movie.tmdb_id})
        response = auth_client.delete(url)
        assert response.status_code == status.HTTP_204_NO_CONTENT

    def test_user_cannot_remove_another_users_watchlist_item(self, auth_client, other_user):
        url = reverse('user-watchlist-list', kwargs={'username': other_user.username})
        response = auth_client.delete(url)
        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED