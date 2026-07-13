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

    def test_genre_movies_relationship(self, genre_factory, movie_factory):
        genre = genre_factory(tmdb_id=50, name='Science Fiction')
        movie = movie_factory(tmdb_id=999, title='Inception', genres=[genre])
        assert movie in genre.movies.all()



"""
Movie Model
"""
@pytest.mark.django_db
class TestMovieModel:

    def test_string_representation_returns_movie_title(self, movie_factory):
        movie = movie_factory(tmdb_id='19542', title='The Red Shoes')
        assert str(movie) == 'The Red Shoes'

    def test_unique_tmdb_id(self, movie_factory):
        movie_factory(tmdb_id=550, title='Fight Club')
        from movies.models import Movie
        with pytest.raises(IntegrityError):
            Movie.objects.create(tmdb_id=550, title='Duplicate')

    def test_release_date_is_nullable(self, movie_factory):
        movie = movie_factory(tmdb_id=2500, title='Hello Movie')
        assert movie.release_date is None

    def test_created_at_is_auto_set(self, movie_factory):
        movie = movie_factory()
        assert movie.created_at is not None

    def test_movie_genres_m2m_relationship(self, movie_factory, genre_factory):
        g1 = genre_factory(tmdb_id=10, name='Action')
        g2 = genre_factory(tmdb_id=20, name='Thriller')
        movie = movie_factory(tmdb_id=777, title='John Wick', genres=[g1, g2])
        assert movie.genres.count() == 2
        assert g1 in movie.genres.all()
        assert g2 in movie.genres.all()