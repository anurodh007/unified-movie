"""
Tests recommendations/algorithms/content_based/*.py
"""

import pytest
import numpy as np
from unittest.mock import patch, MagicMock

from recommendations.algorithms.content_based.movie_vectors import (
    build_movie_vector,
    build_all_movie_vectors
)
from recommendations.algorithms.content_based.user_vectors import build_user_vector
from recommendations.algorithms.content_based.similarity import calculate_similarity
from recommendations.algorithms.content_based.ranking import rank_filter_recommendations



"""
build_movie_vector
"""
@pytest.mark.django_db
class TestBuildMovieVector:

    def test_vector_length_equals_genre_count(self, movie_factory, genre_factory):
        action = genre_factory(tmdb_id=28, name='Action')
        drama = genre_factory(tmdb_id=18, name='Drama')
        comedy = genre_factory(tmdb_id=40, name='Comedy')
        master = ['Action', 'Comedy', 'Drama']
        movie = movie_factory(tmdb_id=101, title='A', genres=[action, comedy])
        vector = build_movie_vector(movie, master)
        assert len(vector) == 3

    def test_genre_present_in_vector(self, movie_factory, genre_factory):
        action = genre_factory(tmdb_id=28, name='Action')
        drama = genre_factory(tmdb_id=18, name='Drama')
        master = ['Action', 'Drama']
        movie = movie_factory(tmdb_id=201, title='B', genres=[drama])
        vector = build_movie_vector(movie, master)
        assert vector[1] == 1

    def test_empty_genres_gives_zero_vector(self, movie_factory, genre_factory):
        genre_factory(tmdb_id=28, name='Action')
        genre_factory(tmdb_id=40, name='Comedy')
        genre_factory(tmdb_id=18, name='Drama')
        master = ['Action', 'Comedy', 'Drama']
        movie = movie_factory(tmdb_id=301, title='C', genres=[])
        vector = build_movie_vector(movie, master)
        assert np.all(vector == 0)



"""
build_all_movie_vectors
"""
@pytest.mark.django_db
class TestBuildAllMovieVectors:

    TARGET_CACHE_STRING = 'recommendations.algorithms.content_based.movie_vectors.cache'

    def test_returns_dict_with_tmdb_id_as_keys(self, movie_factory, genre_factory):
        action = genre_factory(tmdb_id=28, name='Action')
        movie_factory(tmdb_id=101, title='A', genres=[action])
        with patch(self.TARGET_CACHE_STRING) as mock_cache:
            mock_cache.get.return_value = None
            result = build_all_movie_vectors()
        assert 101 in result
        assert 'movie' in result[101]
        assert 'vector' in result[101]
        assert 'norm' in result[101]

    def test_returns_cached_data_on_hit(self, db):
        fake = {
            201: {
                'movie': MagicMock(),
                'vector': np.array([1, 0]),
                'norm': 1.0,
            },
        }
        with patch(self.TARGET_CACHE_STRING) as mock_cache:
            mock_cache.get.return_value = fake
            result = build_all_movie_vectors()
        assert result == fake



"""
build_user_vector
"""
@pytest.mark.django_db
class TestBuildUserVector:
    
    TARGET_CACHE_STRING = 'recommendations.algorithms.content_based.user_vectors.cache'

    def test_cold_start_returns_zero_vector(self, user, genre_factory):
        genre_factory(tmdb_id=28, name='Action')
        with patch(self.TARGET_CACHE_STRING) as mock_cache:
            mock_cache.get.return_value = None
            vector = build_user_vector(user)
        assert np.all(vector == 0)

    def test_user_vector_built_from_high_ratings(self, user, movie_factory, genre_factory, review_factory):
        action = genre_factory(tmdb_id=28, name='Action')
        movie = movie_factory(tmdb_id=101, title='Highly Rated', genres=[action])
        review_factory(user=user, movie=movie, rating=9)
        with patch(self.TARGET_CACHE_STRING) as mock_cache:
            mock_cache.get.return_value = None
            vector = build_user_vector(user)
        assert np.any(vector > 0)

    def test_user_vector_excludes_low_ratings(self, user, movie_factory, genre_factory, review_factory):
        comedy = genre_factory(tmdb_id=40, name='Comedy')
        movie = movie_factory(tmdb_id=201, title='Low Rated', genres=[comedy])
        review_factory(user=user, movie=movie, rating=5)
        with patch(self.TARGET_CACHE_STRING) as mock_cache:
            mock_cache.get.return_value = None
            vector = build_user_vector(user)
        assert np.all(vector == 0)



"""
calculate_similarity
"""
class TestContentBasedSimilarity:

    TARGET_CACHE_STRING = 'recommendations.algorithms.content_based.similarity.cache'

    def test_identical_vectors_score_1(self):
        user = MagicMock()
        user.id = 25
        user_vector = np.array([1.0, 0.0, 1.0])
        movie_vectors = {
            101: {
                'movie': MagicMock(),
                'vector': np.array([1.0, 0.0, 1.0]),
                'norm': float(np.linalg.norm([1.0, 0.0, 1.0])),
            }
        }
        with patch(self.TARGET_CACHE_STRING) as mock_cache:
            mock_cache.get.return_value = None
            scores = calculate_similarity(user, user_vector, movie_vectors)
        assert scores[101]['score'] == pytest.approx(1.0)

    def test_orthogonal_vectors_score_0(self):
        user = MagicMock()
        user.id = 10
        user_vector = np.array([1.0, 0.0, 0.0])
        movie_vectors = {
            201: {
                'movie': MagicMock(),
                'vector': np.array([0.0, 1.0, 0.0]),
                'norm': 1.0
            }
        }
        with patch(self.TARGET_CACHE_STRING) as mock_cache:
            mock_cache.get.return_value = None
            scores = calculate_similarity(user, user_vector, movie_vectors)
        assert scores[201]['score'] == pytest.approx(0.0)

    def test_zero_user_vector_scores_0(self):
        user = MagicMock()
        user.id = 5
        user_vector = np.array([0.0, 0.0, 0.0])
        movie_vectors = {
            301: {
                'movie': MagicMock(),
                'vector': np.array([1.0, 1.0, 0.0]),
                'norm': float(np.linalg.norm([1.0, 1.0, 0.0]))
            }
        }
        with patch(self.TARGET_CACHE_STRING) as mock_cache:
            mock_cache.get.return_value = None
            scores = calculate_similarity(user, user_vector, movie_vectors)
        assert scores[301]['score'] == pytest.approx(0.0)

    def test_cache_hit_skips_computation(self):
        user = MagicMock()
        user.id = 7
        fake = {
            401: {
                'movie': MagicMock(),
                'score': 0.9
            }
        }
        with patch(self.TARGET_CACHE_STRING) as mock_cache:
            mock_cache.get.return_value = fake
            result = calculate_similarity(user, np.zeros(3), {})
        assert result == fake



"""
rank_filter_recommendations
"""
@pytest.mark.django_db
class TestRankFilterRecommendations:

    def test_excludes_reviewed_movies(self, user, movie_factory, review_factory):
        movie = movie_factory(tmdb_id=2500, title='Reviewed Film')
        review_factory(user=user, movie=movie, rating=9)
        scores = {
            2500: {
                'movie': movie,
                'score': 0.85
            }
        }
        result = rank_filter_recommendations(user, scores, limit=10)
        assert all(r['tmdb_id'] != 2500 for r in result)

    def test_excludes_watchlisted_movies(self, user, movie_factory, watchlist_factory):
        movie = movie_factory(tmdb_id=5001, title='Watchlisted Film')
        watchlist_factory(user=user, movie=movie)
        scores = {
            5001: {
                'movie': movie,
                'score': 0.72
            }
        }
        result = rank_filter_recommendations(user, scores, limit=10)
        assert all(r['tmdb_id'] != 5001 for r in result)

    def test_respects_recommendation_limit(self, user, movie_factory):
        import random
        scores = {}
        for i in range(20):
            movie = movie_factory(tmdb_id=i + 100)
            score = random.uniform(0.5, 0.99)
            scores[i+100] = {
                'movie': movie,
                'score': score
            }
        result = rank_filter_recommendations(user, scores, limit=10)
        assert len(result) <= 10

    def test_sorts_results_by_similarity_desc(self, user, movie_factory):
        scores = {
            101: {
                'movie': movie_factory(tmdb_id=101, title='Low Score'),
                'score': 0.75
            },
            201: {
                'movie': movie_factory(tmdb_id=201, title='High Score'),
                'score': 0.95
            }
        }
        result = rank_filter_recommendations(user, scores, limit=10)
        assert result[0]['score'] > result[-1]['score']