"""
Integration test for content-based recommendation pipeline

User Authentication --> Watchlist --> Reviews --> Recommendation
"""

import pytest
from rest_framework import status
from rest_framework.test import APIClient

from movies.models import Movie

def reviews_url(tmdb_id):
    return f'/api/movies/{tmdb_id}/reviews/'

WATCHLIST_URL = '/api/watchlist/'

RECOMMENDATION_URL = '/api/recommendations/'


@pytest.mark.django_db
@pytest.mark.slow
class TestContentBasedPipeline:

    def test_entire_content_based_flow(self, content_based_dataset):
        user = content_based_dataset['user']

        client = APIClient()
        client.force_authenticate(user)

        watchlisted_ids = {101, 102, 201, 202, 301}
        movies = Movie.objects.filter(tmdb_id__in=watchlisted_ids)
        for movie in movies:
            watchlist_response = client.post(WATCHLIST_URL, {'tmdb_id': movie.tmdb_id}, format='json')
            assert watchlist_response.status_code == status.HTTP_201_CREATED

        response = client.get(WATCHLIST_URL)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 5

        reviewed_ids = {101, 105, 207, 304}
        ratings = {
            101: 10,
            105: 8,
            207: 5,
            304: 9
        }
        movies = Movie.objects.filter(tmdb_id__in=reviewed_ids)
        for movie in movies:
            review_response = client.post(
                reviews_url(movie.tmdb_id),
                {'review_text': 'Nice film', 'rating': ratings[movie.tmdb_id]},
                format='json'
            )
            assert review_response.status_code == status.HTTP_201_CREATED
        
        recommendation_response = client.get(RECOMMENDATION_URL)
        assert recommendation_response.status_code == status.HTTP_200_OK
        assert 'results' in recommendation_response.data
        
        results = recommendation_response.data['results']
        assert len(results) > 0
        excluded_ids = watchlisted_ids | reviewed_ids
        assert all(r['tmdb_id'] not in excluded_ids for r in results)