"""
Tests for User API

Endpoints under test:

POST /api/users/register/

GET /api/users/<str:username>/
GET /api/users/<str:username>/reviews/
"""

import pytest
from django.urls import reverse
from rest_framework import status



"""
User API Tests
"""
@pytest.mark.django_db
class TestUserAPI:

    def test_register_with_valid_data_returns_201(self, api_client):
        data = {
            'username': 'newuser',
            'email': 'newuser@mail.com',
            'password': 'StrongPass123!',
            'confirm_password': 'StrongPass123!',
        }
        response = api_client.post(
            reverse('register'),
            data,
            format='json'
        )
        assert response.status_code == status.HTTP_201_CREATED

    def test_authenticated_user_profile_uses_owner_serializer(self, auth_client, user):
        url = reverse('user_detail', kwargs={'username': user.username})
        response = auth_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert 'email' in response.data

    def test_nonexistent_username_returns_404(self, api_client):
        url = reverse('user_detail', kwargs={'username': 'no_user'})
        response = api_client.get(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND



"""
User Subresources API Tests (Reviews, Comments, Likes)
"""
@pytest.mark.django_db
class TestUserSubresourcesAPI:

    def test_user_reviews_list(self, api_client, user, movie, review_factory):
        review_factory(user=user, movie=movie)
        response = api_client.get(reverse('user-reviews-list', kwargs={'username': user.username}))
        assert response.status_code == status.HTTP_200_OK

    def test_user_reviews_filtered_by_username(self, api_client, user, other_user, movie_factory, review_factory):
        movie1 = movie_factory(tmdb_id=1001, title='User Movie')
        movie2 = movie_factory(tmdb_id=2001, title='Other Movie')
        review_factory(user=user, movie=movie1)
        review_factory(user=other_user, movie=movie2)
        
        response = api_client.get(reverse('user-reviews-list', kwargs={'username': user.username}))
        assert response.status_code == status.HTTP_200_OK
        usernames = {r['user'] for r in response.data['results']}
        assert usernames == {user.username}