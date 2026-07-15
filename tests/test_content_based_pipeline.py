"""
Integration test for content-based recommendation pipeline

User Authentication --> Watchlist --> Reviews --> Recommendation
"""

import pytest
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient

from movies.models import Movie, Genre

User = get_user_model()

def reviews_url(tmdb_id):
    return f'/api/movies/{tmdb_id}/reviews/'

WATCHLIST_URL = '/api/watchlist/'

RECOMMENDATION_URL = '/api/recommendations/'


@pytest.mark.django_db
@pytest.mark.slow
class TestContentBasedPipeline(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username='test', email='test@mail.com', password='StrongPass123!')
        cls.action = Genre.objects.create(tmdb_id='28', name='Action')
        cls.comedy = Genre.objects.create(tmdb_id='40', name='Comedy')
        cls.drama = Genre.objects.create(tmdb_id='18', name='Drama')

        for i in range(1, 11):
            movie = Movie.objects.create(tmdb_id=i + 100, title=f'Movie {i}')
            movie.genres.add(cls.action, cls.comedy)
        for i in range(1, 11):
            movie = Movie.objects.create(tmdb_id=i + 200, title=f'Movie {i + 10}')
            movie.genres.add(cls.action, cls.drama)
        for i in range(1, 11):
            movie = Movie.objects.create(tmdb_id=i + 300, title=f'Movie {i + 20}')
            movie.genres.add(cls.comedy, cls.drama)

    def test_entire_content_based_flow(self):
        client = APIClient()
        client.force_authenticate(self.user)

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