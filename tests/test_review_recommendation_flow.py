"""
Integration Test for Authentication --> Review API --> Recommendation Service
"""

import pytest
from rest_framework.test import APIClient
from django.urls import reverse

def reviews_url(tmdb_id):
    return f'/api/movies/{tmdb_id}/reviews/'


@pytest.mark.django_db
class TestRecommendationIntegration:

    def test_recommendations_after_review(self, user, movie):
        """
        User logs in, creates a review, then requests recommendations.
        """

        client = APIClient()
        client.force_authenticate(user)

        review_data = {
            'rating': 5,
            'review_text': 'Excellent movie!'
        }

        review_response = client.post(
            reviews_url(movie.tmdb_id),
            review_data,
            format='json'
        )

        assert review_response.status_code == 201

        recommendation_url = '/api/recommendations/'

        recommendation_response = client.get(
            recommendation_url
        )

        assert recommendation_response.status_code == 200

        for field in ('count', 'next', 'previous', 'results'):
            assert field in recommendation_response.data