"""
Tests Review permissions

Endpoints under test:

GET /api/movies/<int:tmdb_id>/reviews/
POST /api/movies/<int:tmdb_id>/reviews/

GET /api/movies/<int:tmdb_id>/reviews/<int:review_id>/
PUT /api/movies/<int:tmdb_id>/reviews/<int:review_id>/
PATCH /api/movies/<int:tmdb_id>/reviews/<int:review_id>/
DELETE /api/movies/<int:tmdb_id>/reviews/<int:review_id>/
"""

import pytest
from django.urls import reverse
from rest_framework import status
from reviews.models import Review


"""
Review Permission Tests
"""
@pytest.mark.django_db
class TestReviewPermission:

    def test_anonymous_user_can_view_reviews(self, api_client, movie):
        url = reverse('reviews:movie-reviews-list', kwargs={'tmdb_id': movie.tmdb_id})
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK

    def test_anonymous_user_cannot_create_review(self, api_client, movie):
        url = reverse('reviews:movie-reviews-list', kwargs={'tmdb_id': movie.tmdb_id})
        response = api_client.post(url, {'review_text': 'Nice Movie', 'rating': 8}, format='json')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_authenticated_user_can_create_review(self, auth_client, movie):
        url = reverse('reviews:movie-reviews-list', kwargs={'tmdb_id': movie.tmdb_id})
        response = auth_client.post(url, {'review_text': 'Nice Movie', 'rating': 8}, format='json')
        assert response.status_code == status.HTTP_201_CREATED
    
    def test_review_owner_can_update_review(self, auth_client, user, movie):
        review = Review.objects.create(user=user, movie=movie, review_text='Nice', rating=8)
        url = reverse('reviews:review-detail', kwargs={'tmdb_id': movie.tmdb_id, 'review_id': review.pk})
        response = auth_client.patch(url, {'rating': 7}, format='json')
        assert response.status_code == status.HTTP_200_OK
        review.refresh_from_db()
        assert review.rating == 7
        assert review.review_text == 'Nice'

    def test_review_owner_can_delete_review(self, auth_client, user, movie):
        review = Review.objects.create(user=user, movie=movie, review_text='Nice', rating=8)
        url = reverse('reviews:review-detail', kwargs={'tmdb_id': movie.tmdb_id, 'review_id': review.pk})
        response = auth_client.delete(url)
        assert response.status_code == status.HTTP_204_NO_CONTENT

    def test_user_cannot_update_another_users_review(self, auth_client, other_user, movie):
        review = Review.objects.create(user=other_user, movie=movie, review_text='Great film!', rating=7)
        url = reverse('reviews:review-detail', kwargs={'tmdb_id': movie.tmdb_id, 'review_id': review.pk})
        response = auth_client.put(url, {'review_text': 'Poor Taste', 'rating': 3}, format='json')
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_user_cannot_delete_another_users_review(self, auth_client, other_user, movie):
        review = Review.objects.create(user=other_user, movie=movie, review_text='Great film!', rating=7)
        url = reverse('reviews:review-detail', kwargs={'tmdb_id': movie.tmdb_id, 'review_id': review.pk})
        response = auth_client.delete(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_anonymous_user_can_view_user_reviews(self, api_client, user, movie):
        review = Review.objects.create(user=user, movie=movie, review_text='Nice film!', rating=8)
        url = reverse('reviews:review-detail', kwargs={'tmdb_id': movie.tmdb_id, 'review_id': review.pk})
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK

    def test_anonymous_user_cannot_update_delete_user_reviews(self, api_client, user, movie):
        review = Review.objects.create(user=user, movie=movie, review_text='Nice film!', rating=8)
        url = reverse('reviews:review-detail', kwargs={'tmdb_id': movie.tmdb_id, 'review_id': review.pk})
        response = api_client.patch(url, {'rating': 9}, format='json')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        response = api_client.delete(url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED