"""
Testing Watchlist serializer

Covers:
    - Serializes valid data
    - tmdb_id required
"""

import pytest
from watchlist.serializers import WatchlistSerializer


class TestWatchlistSerializer:

    @pytest.mark.django_db
    def test_serializes_watchlist_items(self, user_factory, movie_factory, watchlist_factory):
        user = user_factory(username='testuser')
        movie = movie_factory(tmdb_id=550, title='Fight Club')
        wl = watchlist_factory(user=user, movie=movie)
        serializer = WatchlistSerializer(wl)
        assert 'movie' in serializer.data
        assert 'created_at' in serializer.data

    def test_tmdb_id_required_for_write(self):
        serializer = WatchlistSerializer(data={})
        assert not serializer.is_valid()
        assert 'tmdb_id' in serializer.errors