"""
Tests get_recommendations() routing service [content_based vs collaborative]
"""

import pytest
from unittest.mock import patch, MagicMock
from recommendations.services.recommendation import get_recommendations

TARGET_CONTENT_STRING = 'recommendations.services.recommendation.get_recommendations_content'
TARGET_COLLAB_STRING = 'recommendations.services.recommendation.get_recommendations_collab'


"""
get_recommendations() service
"""
@pytest.mark.django_db
class TestGetRecommendationsService:

    def test_cold_start_user_gets_content_based(self, user):
        with patch(TARGET_CONTENT_STRING, return_value=[]) as mock_cb, \
             patch(TARGET_COLLAB_STRING, return_value=[]) as mock_collab:
            get_recommendations(user)
        mock_cb.assert_called_once()
        mock_collab.assert_not_called()

    def test_active_user_gets_collaborative(self, user, movie_factory, review_factory):
        import random
        for i in range(6):
            movie = movie_factory(tmdb_id=i + 100, title=f'Movie {i}')
            review_factory(user=user, movie=movie, rating=random.randint(1, 10))
        fake_collab = [MagicMock()]

        with patch(TARGET_COLLAB_STRING, return_value=fake_collab) as mock_collab, \
             patch(TARGET_CONTENT_STRING, return_value=[]) as mock_cb:
            result = get_recommendations(user)
        assert result == fake_collab
        mock_collab.assert_called_once()
        mock_cb.assert_not_called()

    def test_falls_back_to_content_when_collab_empty(self, user, movie_factory, review_factory):
        import random
        for i in range(6):
            movie = movie_factory(tmdb_id=i + 100, title=f'Movie {i}')
            review_factory(user=user, movie=movie, rating=random.randint(1, 10))
        fake_cb = [MagicMock()]

        with patch(TARGET_COLLAB_STRING, return_value=[]) as mock_collab, \
             patch(TARGET_CONTENT_STRING, return_value=fake_cb) as mock_cb:
            result = get_recommendations(user)
        assert result == fake_cb
        mock_collab.assert_called_once()
        mock_cb.assert_called_once()