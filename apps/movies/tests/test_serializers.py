"""
Testing Genre serializers

Covers:
    - Valid data is serialized
    - Missing data throws errors
"""

import pytest
from movies.serializers.genre_serializer import GenreSerializer


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