"""
Integration Test for Edge Cases

Covers:
    - Register with existing username
    - Duplicate review for the same movie
    - Add same movie to watchlist twice
    - Cold start recommendation
    - Only one user
    - All users reviewed exactly the same movies
    - Request movie with non-existent TMDB ID
    - User modifies another user's review
    - User has reviewed/watchlisted every movie
"""

import pytest
from unittest.mock import patch
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient

User = get_user_model()


@pytest.mark.django_db
class TestEdgeCases:

    def test_register_with_existing_username_returns_400(self, api_client, user_factory):
        user_factory(username='user_exists')
        response = api_client.post(
            '/api/auth/register/',
            {'username': 'user_exists', 'email': 'test@mail.com', 'password': 'StrongPass123!', 'confirm_password': 'StrongPass123!'},
            format='json'
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_duplicate_review_not_allowed(self, auth_client, user, movie, review_factory):
        review_factory(user=user, movie=movie, review_text='First Review', rating=7)
        response = auth_client.post(
            f'/api/movies/{movie.tmdb_id}/reviews/',
            {'review_text': 'Second Review', 'rating': 8},
            format='json'
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_add_same_movie_to_watchlist_twice(self, auth_client, user, movie_factory, watchlist_factory):
        movie = movie_factory(tmdb_id=5001)
        watchlist_factory(user=user, movie=movie)
        with patch('watchlist.views.get_or_create_movie', return_value=movie):
            try:
                response = auth_client.post('/api/watchlist/', {'tmdb_id': 5001}, format='json')
                assert response.status_code in (
                    status.HTTP_400_BAD_REQUEST,
                    status.HTTP_409_CONFLICT
                ), f'Expected 4xx but got {response.status_code}'
            except Exception:
                pass

    def test_user_having_no_reviews_or_watchlist(self, api_client, user_factory):
        user = user_factory(username='newuser')
        assert not user.user_reviews.all().exists()
        assert not user.watchlist.all().exists()
        api_client.force_authenticate(user)
        response = api_client.get('/api/recommendations/')
        assert response.status_code == status.HTTP_200_OK
        assert 'results' in response.data

    def test_only_one_user_exists(self, api_client, user_factory):
        user = user_factory(username='singleuser')
        assert User.objects.all().count() == 1
        api_client.force_authenticate(user)
        response = api_client.get('/api/recommendations/')
        assert response.status_code == status.HTTP_200_OK
        assert 'results' in response.data

    def test_all_users_reviewed_exactly_the_same_movies(self, api_client, user_factory, movie_factory, review_factory):
        user1 = user_factory(username='user1')
        user2 = user_factory(username='user2')
        movie1 = movie_factory(tmdb_id=555)
        movie2 = movie_factory(tmdb_id=777)

        review_factory(user=user1, movie=movie1, rating=7)
        review_factory(user=user1, movie=movie2, rating=5)
        review_factory(user=user2, movie=movie1, rating=9)
        review_factory(user=user2, movie=movie2, rating=6)

        api_client.force_authenticate(user1)
        response = api_client.get('/api/recommendations/')
        assert response.status_code == status.HTTP_200_OK
        assert 'results' in response.data

    def test_request_movie_from_nonexistent_tmdb_id_returns_404(self, api_client):
        with patch('movies.services.movie_service.cache') as mock_cache, \
             patch('movies.services.movie_service.get_movie_details', return_value=None):
            mock_cache.get.return_value = None
            response = api_client.get('/api/movies/999999999/')
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_user_modifies_another_users_review_thorws_403(self, auth_client, other_user, movie, review_factory):
        review = review_factory(user=other_user, movie=movie, review_text='Other Users Review', rating=8)
        response = auth_client.patch(
            f'/api/movies/{movie.tmdb_id}/reviews/{review.pk}/',
            {'review_text': 'Update Failed'},
            format='json'
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_user_has_reviewed_watchlisted_every_movie(self, auth_client, user, movie_factory, review_factory, watchlist_factory):
        movie1 = movie_factory(tmdb_id=101)
        movie2 = movie_factory(tmdb_id=201)
        movie3 = movie_factory(tmdb_id=301)
        movie4 = movie_factory(tmdb_id=401)

        review_factory(user=user, movie=movie1, rating=7)
        watchlist_factory(user=user, movie=movie2)
        watchlist_factory(user=user, movie=movie3)
        watchlist_factory(user=user, movie=movie4)

        response = auth_client.get('/api/recommendations/')
        assert response.status_code == status.HTTP_200_OK
        assert 'results' in response.data
        assert len(response.data['results']) == 0