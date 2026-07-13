"""
Testing Review and Like serializers

Covers:
    - Validate rating
    - Missing review text
"""

import pytest
from unittest.mock import MagicMock
from rest_framework.test import APIRequestFactory

from reviews.serializers.review_serializer import ReviewSerializer
from reviews.serializers.like_comment_serializer import LikeSerializer
from reviews.models import ReviewLike

factory = APIRequestFactory()


"""
Review serializer
"""
class TestReviewSerializer:

    @pytest.mark.django_db
    def test_valid_rating_passes(self, user, movie, review_factory):
        review = review_factory(user=user, movie=movie, review_text='Great movie', rating=8)
        request = factory.get('/')
        request.user = user
        serializer = ReviewSerializer(
            review,
            context={'request': request}
        )
        assert serializer.data['rating'] == 8

    def test_rating_0_fails_validation(self):
        serializer = ReviewSerializer(data={'review_text': 'Nice', 'rating': 0})
        assert not serializer.is_valid()
        assert 'rating' in serializer.errors

    def test_rating_11_fails_validation(self):
        serializer = ReviewSerializer(data={'review_text': 'Test', 'rating': 11})
        assert not serializer.is_valid()
        assert 'rating' in serializer.errors

    def test_missing_review_text_fails(self):
        serializer = ReviewSerializer(data={'rating': 11})
        assert not serializer.is_valid()
        assert 'review_text' in serializer.errors


"""
Like serializer
"""
class TestLikeSerializer:

    @pytest.mark.django_db
    def test_duplicate_like_raises_validation_error(self, user, movie, review_factory):
        review = review_factory(user=user, movie=movie)
        ReviewLike.objects.create(user=user, review=review)

        view_mock = MagicMock()
        view_mock.kwargs = {'review_id': review.pk}
        request_mock = MagicMock()
        request_mock.user = user

        serializer = LikeSerializer(
            data={},
            context={'request': request_mock, 'view': view_mock}
        )
        assert not serializer.is_valid()