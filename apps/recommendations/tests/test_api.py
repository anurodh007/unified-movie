"""
API tests for recommendations

Endpoints under test:

GET  /api/recommendations/
"""

import pytest
from unittest.mock import patch
from rest_framework import status

RECOMMENDATIONS_URL = '/api/recommendations/'


@pytest.mark.django_db
class TestRecommendationAPI:

    def test_authenticated_user_gets_200(self, auth_client):
        with patch(
            'recommendations.views.get_recommendations',
            return_value=[]
        ):
            response = auth_client.get(RECOMMENDATIONS_URL)
        assert response.status_code == status.HTTP_200_OK

    def test_response_is_paginated(self, auth_client, movie_factory):
        movies = [movie_factory(tmdb_id=5000 + i, title=f'Rec{i}') for i in range(15)]
        fake_recs = [
            {
                'tmdb_id': m.tmdb_id,
                'movie': m,
                'score': (15 - i),
                'recommendation_type': 'content_based'
            }
            for i, m in enumerate(movies)
        ]
        with patch(
            'recommendations.views.get_recommendations',
            return_value=fake_recs
        ):
            response = auth_client.get(RECOMMENDATIONS_URL)
        assert response.status_code == status.HTTP_200_OK
        assert 'results' in response.data
        assert len(response.data['results']) <= 10

    def test_serializer_fields_are_present(self, auth_client, movie_factory):
        movie = movie_factory(tmdb_id=101, title='Rec Movie')
        fake_recs = [
            {
                'tmdb_id': movie.tmdb_id,
                'movie': movie,
                'score': 0.95,
                'recommendation_type': 'content_based',
            }
        ]
        with patch('recommendations.views.get_recommendations', return_value=fake_recs):
            response = auth_client.get(RECOMMENDATIONS_URL)
        assert response.status_code == status.HTTP_200_OK
        if response.data['results']:
            item = response.data['results'][0]
            for field in ('tmdb_id', 'title', 'average_rating', 'score', 'recommendation_type'):
                assert field in item