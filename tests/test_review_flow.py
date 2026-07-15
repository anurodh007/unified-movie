"""
Integration Tests for Review CRUD
"""

import pytest
from rest_framework import status
from rest_framework.test import APIClient

def reviews_url(tmdb_id):
    return f'/api/movies/{tmdb_id}/reviews/'

def review_detail_url(tmdb_id, review_id):
    return f'/api/movies/{tmdb_id}/reviews/{review_id}/'


@pytest.mark.django_db
class TestReviewFlow:

    def test_login_create_update_delete_review(self, user_factory, movie_factory):
        user = user_factory(username='newuser', email='newuser@mail.com')
        movie = movie_factory(tmdb_id=101, title='New Movie')

        client = APIClient()
        client.force_authenticate(user)

        response = client.post(
            reviews_url(movie.tmdb_id),
            {'review_text': 'Nice Film!', 'rating': 8},
            format='json'
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['review_text'] == 'Nice Film!'

        response = client.get(
            reviews_url(movie.tmdb_id)
        )
        assert response.data['count'] >= 1
        assert 'results' in response.data
        results = response.data['results']
        review_id = results[0]['id']

        response = client.get(
            review_detail_url(movie.tmdb_id, review_id)
        )
        assert response.data['rating'] == 8

        response = client.patch(
            review_detail_url(movie.tmdb_id, review_id),
            {'review_text': 'Updated Review'},
            format='json'
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data['review_text'] == 'Updated Review'

        response = client.delete(
            review_detail_url(movie.tmdb_id, review_id)
        )
        assert response.status_code == status.HTTP_204_NO_CONTENT