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



"""
calculate_similarity
"""
class TestCollabSimilarity:

    TARGET_CACHE_STRING = 'recommendations.algorithms.collaborative.similarity.cache'

    def test_user_with_no_ratings_returns_empty(self):
        user = MagicMock()
        user.id = 999
        user_matrix = {
            'matrix': np.array([[1, 2], [3, 4]]),
            'user_index': {1: 0, 2: 1}
        }
        with patch(self.TARGET_CACHE_STRING) as mock_cache:
            mock_cache.get.return_value = None
            result = calculate_similarity(user, user_matrix)
        assert result == {}

    def test_self_excluded_from_scores(self):
        user = MagicMock()
        user.id = 1
        user_matrix = {
            'matrix': np.array([[7, 8], [6, 9]]),
            'user_index': {1: 0, 2: 1}
        }
        with patch(self.TARGET_CACHE_STRING) as mock_cache:
            mock_cache.get.return_value = None
            result = calculate_similarity(user, user_matrix)
        assert user.id not in result

    def test_identical_ratings_gives_max_similarity(self):
        user = MagicMock()
        user.id = 11
        user_matrix = {
            'matrix': np.array([[7, 8, 9], [8, 7, 9]]),
            'user_index': {11: 0, 22: 1}
        }
        with patch(self.TARGET_CACHE_STRING) as mock_cache:
            mock_cache.get.return_value = None
            result = calculate_similarity(user, user_matrix)
        assert result[22] == pytest.approx(0.99, abs=1e-2)

    def test_cache_hit_returns_cached(self, user):
        fake = {
            11: 0.85,
            12: 0.91,
            13: 0.68
        }
        with patch(self.TARGET_CACHE_STRING) as mock_cache:
            mock_cache.get.return_value = fake
            result = calculate_similarity(user, {})
        assert result == fake



"""
predict_movie_ratings
"""
class TestPredictMovieRatings:

    TARGET_CACHE_STRING = 'recommendations.algorithms.collaborative.prediction.cache'

    def test_user_with_no_rating_returns_empty(self):
        user = MagicMock()
        user.id = 99
        user_matrix = {
            'matrix': np.array([[5, 0], [8, 4]]),
            'user_index': {1: 0, 2: 1},
            'movie_index': {101: 0, 201: 1}
        }
        with patch(self.TARGET_CACHE_STRING) as  mock_cache:
            mock_cache.get.return_value = None
            result = predict_movie_ratings(user, user_matrix, {})
        assert result == {}

    def test_predicts_unrated_movie(self):
        user = MagicMock()
        user.id = 1
        user_matrix = {
            'matrix': np.array([[8, 0], [7, 9]]),
            'user_index': {1: 0, 2: 1},
            'movie_index': {101: 0, 201: 1}
        }
        similarity_scores = {2: 0.62}
        with patch(self.TARGET_CACHE_STRING)as mock_cache:
            mock_cache.get.return_value = None
            result = predict_movie_ratings(user, user_matrix, similarity_scores)
        assert 201 in result
        assert result[201] > 0

    def test_cache_hit_returns_cached(self, user):
        fake = {
            101: 7.89
        }
        with patch(self.TARGET_CACHE_STRING) as mock_cache:
            mock_cache.get.return_value = fake
            result = predict_movie_ratings(user, {}, {})
        assert result == fake



"""
rank_recommendations
"""
@pytest.mark.django_db
class TestRankRecommendations:

    def test_cold_start_returns_empty(self):
        result = rank_recommendations({})
        assert result == []

    def test_sorts_results_predicted_ratings_desc(self, movie_factory):
        movie_factory(tmdb_id=101, title='Low')
        movie_factory(tmdb_id=201, title='High')
        predicted_ratings = {
            101: 7.5,
            201: 9.0
        }
        result = rank_recommendations(predicted_ratings)
        assert result[0]['score'] > result[-1]['score']

    def test_respects_recommendation_limits(self, movie_factory):
        import random
        predicted_ratings = {}
        for i in range(20):
            movie_factory(tmdb_id=1000 + i, title=f'Collab Movie {i + 1}')
            predicted_ratings[1000 + i] = random.uniform(5.0, 10.0)
        result = rank_recommendations(predicted_ratings, limit=10)
        assert len(result) <= 10