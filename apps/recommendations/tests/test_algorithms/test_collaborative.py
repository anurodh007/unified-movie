"""
Tests recommendations/algorithms/collaborative/*.py
"""

import pytest
import numpy as np
from unittest.mock import patch, MagicMock

from recommendations.algorithms.collaborative.user_matrix import build_user_matrix
from recommendations.algorithms.collaborative.similarity import calculate_similarity
from recommendations.algorithms.collaborative.prediction import predict_movie_ratings
from recommendations.algorithms.collaborative.ranking import rank_recommendations



"""
build_user_matrix
"""
@pytest.mark.django_db
class TestBuildUserMatrix:

    TARGET_CACHE_STRING = 'recommendations.algorithms.collaborative.user_matrix.cache'

    def test_matrix_shape(self, user, movie_factory, review_factory):
        movie = movie_factory(tmdb_id=101, title='A')
        review_factory(user=user, movie=movie, rating=8)
        with patch(self.TARGET_CACHE_STRING) as mock_cache:
            mock_cache.get.return_value = None
            result = build_user_matrix()
        matrix = result['matrix']
        assert matrix.shape[0] >= 1
        assert matrix.shape[1] >= 1

    def test_rating_placed_correctly(self, user, movie_factory, review_factory):
        movie = movie_factory(tmdb_id=201, title='B')
        review_factory(user=user, movie=movie, rating=8)
        with patch(self.TARGET_CACHE_STRING) as mock_cache:
            mock_cache.get.return_value = None
            result = build_user_matrix()
        matrix = result['matrix']
        user_idx = result['user_index'][user.id]
        movie_idx = result['movie_index'][movie.tmdb_id]
        assert matrix[user_idx][movie_idx] == pytest.approx(8.0)

    def test_cache_hit_returns_cached(self, db):
        fake = {
            'matrix': np.zeros((3, 3)),
            'user_index': {10: 0, 20: 1, 30: 2},
            'movie_index': {555: 0, 777: 1, 888: 2},
        }
        with patch(self.TARGET_CACHE_STRING) as mock_cache:
            mock_cache.get.return_value = fake
            result = build_user_matrix()
        assert result == fake