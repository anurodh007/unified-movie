"""
Test Genre, Movie, StreamingPlatform Models

Covers:
    - String representation(__str__)
    - Field constraints
    - Relationships (Foreign Key, M2M)
"""


import pytest
from django.db import IntegrityError


"""
Genre Model
"""
@pytest.mark.django_db
class TestGenreModel:

    def test_string_representation_returns_genre_name(self, genre_factory):
        genre = genre_factory(tmdb_id=25, name='Western')
        assert str(genre) == 'Western'

    def test_genre_tmdb_id_is_unique(self, genre_factory):
        genre_factory(tmdb_id=10, name='Action')
        from movies.models import Genre
        with pytest.raises(IntegrityError):
            Genre.objects.create(tmdb_id=10, name='Adventure')