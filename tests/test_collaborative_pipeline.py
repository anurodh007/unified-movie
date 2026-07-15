"""
Integration test for collaborative recommendation.

Multiple Users --> Multiple Movies --> Multiple Reviews --> KNN --> Recommendation
"""

import pytest
import random
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient

from reviews.models import Review

User = get_user_model()

RECOMMENDATION_URL = '/api/recommendations/'


@pytest.mark.django_db
@pytest.mark.slow
class TestCollaborativePipeline:

    def test_entire_collab_flow(self, collab_dataset):
        rd = random.Random(42)
        movies = collab_dataset['movies']

        new_user = User.objects.create_user(username='newuser', email='newuser@mail.com', password='StrongPass123!')

        chosen_movies = rd.sample(list(movies), 10)
        reviewed_tmdb_ids = {movie.tmdb_id for movie in chosen_movies}

        for movie in chosen_movies: 
            Review.objects.create(
                user=new_user,
                movie=movie,
                rating=rd.randint(1, 10),
            )

        client = APIClient()
        client.force_authenticate(new_user)

        recommendation_response = client.get(RECOMMENDATION_URL)
        assert recommendation_response.status_code == status.HTTP_200_OK
        assert 'results' in recommendation_response.data

        results = recommendation_response.data['results']
        assert all(
            recommendation['tmdb_id'] not in reviewed_tmdb_ids
            for recommendation in results
        )