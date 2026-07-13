"""
Test Recommendation serializer
"""

import pytest
from recommendations.serializers import RecommendationSerializer


class TestRecommendationSerializer:

    @pytest.mark.django_db
    def test_valid_recommendations(self, movie_factory):
        movie = movie_factory(tmdb_id=5001, title='Recommended Movie')
        data = {
            'tmdb_id': movie.tmdb_id,
            'movie': movie,
            'score': 0.85,
            'recommendation_type': 'content_based'
        }
        serializer = RecommendationSerializer(data)
        for field in ('tmdb_id', 'title', 'score', 'recommendation_type'):
            assert field in serializer.data