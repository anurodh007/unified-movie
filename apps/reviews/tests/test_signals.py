"""
Testing movie stats signals

Covers:
    - Updating average_rating and vote_count on review creation/deletion
"""

import pytest


@pytest.mark.django_db
class TestMovieStatsSignal:

    def test_average_rating_updated_on_review_create(self, user_factory, movie_factory, review_factory):
        user = user_factory(username='alice')
        movie = movie_factory(tmdb_id=111, title='The General', average_rating=0)
        review = review_factory(user=user, movie=movie, rating=10)
        movie.refresh_from_db()
        assert movie.average_rating == pytest.approx(10)
        assert movie.vote_count == 1

    def test_vote_count_updated_on_review_delete(self, user_factory, movie_factory, review_factory):
        user = user_factory(username='charlie')
        movie = movie_factory(tmdb_id=111, title='City Lights', average_rating=0)
        review = review_factory(user=user, movie=movie, rating=10)
        movie.refresh_from_db()
        assert movie.vote_count == 1
        review.delete()
        movie.refresh_from_db()
        assert movie.vote_count == 0
        