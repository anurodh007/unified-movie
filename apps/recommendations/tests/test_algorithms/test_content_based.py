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