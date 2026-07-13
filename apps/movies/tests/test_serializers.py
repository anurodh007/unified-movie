"""
Testing Genre, Movie serializers

Covers:
    - Valid data is serialized
    - Missing data throws errors
"""

import pytest
from movies.serializers.genre_serializer import GenreSerializer
from movies.serializers.movie_serializer import MovieListSerializer, MovieDetailSerializer


"""
Genre serializer
"""
class TestGenreSerializer:

    @pytest.mark.django_db
    def test_valid_data_serializes(self, genre_factory):
        genre = genre_factory(tmdb_id=28, name='Action')
        serializer = GenreSerializer(genre)
        assert serializer.data['tmdb_id'] == 28
        assert serializer.data['name'] == 'Action'

    def test_invalid_genre_data(self, db):
        serializer = GenreSerializer(data={})
        assert not serializer.is_valid()


"""
MovieList serializer
"""
class TestMovieListSerializer:

    @pytest.mark.django_db
    def test_serializes_movie(self, movie_factory):
        movie = movie_factory(tmdb_id=550, title='Fight Club')
        serializer = MovieListSerializer(movie)
        for field in ('tmdb_id', 'title', 'popularity', 'average_rating', 'poster_path'):
            assert field in serializer.data

    @pytest.mark.django_db
    def test_poster_path_built_correctly(self, movie_factory):
        movie = movie_factory(tmdb_id=111, title='Beautiful Boy', poster_path='/abc.jpg')
        serializer = MovieListSerializer(movie)
        poster = serializer.data['poster_path']
        assert '/abc.jpg' in poster
        assert 'image.tmdb.org' in poster


"""
MovieDetail serializer
"""
class TestMovieDetailSerializer:

    @pytest.mark.django_db
    def test_all_fields_are_present(self, movie_factory):
        movie = movie_factory(tmdb_id=550, title='Fight Club')
        serializer = MovieDetailSerializer(movie)
        for field in ('tmdb_id', 'title', 'overview', 'release_date', 'runtime', 'popularity',
            'average_rating', 'vote_count', 'genres', 'poster_path', 'backdrop_path'):
            assert field in serializer.data

    @pytest.mark.django_db
    def test_includes_genres(self, movie_factory, genre_factory):
        action = genre_factory(tmdb_id=28, name='Action')
        movie = movie_factory(tmdb_id=125, title='John Wick', genres=[action])
        serializer = MovieDetailSerializer(movie)
        assert 'genres' in serializer.data
        assert 'Action' in serializer.data['genres']