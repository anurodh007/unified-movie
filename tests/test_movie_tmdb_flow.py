"""
Integration Test for Movies API --> TMDB --> Database 
"""

import pytest
from unittest.mock import patch
from rest_framework import status
from rest_framework.test import APIClient

from movies.models import Movie

def movie_detail_url(tmdb_id):
    return f'/api/movies/{tmdb_id}/'


@pytest.mark.django_db
class TestMovieTMDBFlow:

    def test_movie_tmdb_db_workflow(self, fake_movie_detail, tmdb_id=550):
        client = APIClient()

        assert not Movie.objects.filter(tmdb_id=tmdb_id).exists()

        with patch('apps.movies.services.movie_service.cache') as mock_cache, \
             patch('apps.movies.services.movie_service.get_movie_details', return_value=fake_movie_detail):
            mock_cache.get.return_value = None
            response = client.get(movie_detail_url(tmdb_id))
        
        assert response.data['tmdb_id'] == tmdb_id

        assert Movie.objects.filter(tmdb_id=tmdb_id).exists()