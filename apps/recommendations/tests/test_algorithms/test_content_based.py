"""
Tests recommendations/algorithms/content_based/*.py
"""

import pytest
import numpy as np
from unittest.mock import patch

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