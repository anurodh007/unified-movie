"""
Testing Watchlist model

Covers:
    - One movie per user
    - Cascade delete on user/movie delete
"""

import pytest
from django.db import IntegrityError


@pytest.mark.django_db
class TestWatchlistModel:

    def test_unique_user_movie_watchlist_constraint(self, user_factory, movie_factory, watchlist_factory):
        from watchlist.models import Watchlist
        user = user_factory(username='anurodh')
        movie = movie_factory(tmdb_id=1245, title='Z')
        watchlist = watchlist_factory(user=user, movie=movie)
        with pytest.raises(IntegrityError):
            Watchlist.objects.create(user=user, movie=movie)

    def test_cascade_delete_on_user_delete(self, user_factory, movie_factory, watchlist_factory):
        from watchlist.models import Watchlist
        user = user_factory(username='john')
        movie = movie_factory(tmdb_id=100)
        watchlist = watchlist_factory(user=user, movie=movie)
        user.delete()
        assert not Watchlist.objects.filter(movie=movie).exists()

    def test_cascade_delete_on_movie_delete(self, user_factory, movie_factory, watchlist_factory):
        from watchlist.models import Watchlist
        user = user_factory(username='john')
        movie = movie_factory(tmdb_id=100)
        watchlist = watchlist_factory(user=user, movie=movie)
        movie.delete()
        assert not Watchlist.objects.filter(user=user).exists()