from django.shortcuts import get_object_or_404
from rest_framework import serializers
from reviews.models import Review, ReviewComment, ReviewLike


class CommentSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')

    class Meta:
        model = ReviewComment
        fields = [
            'id',
            'user',
            'comment_text',
            'created_at'
        ]


class LikeSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')

    class Meta:
        model = ReviewLike
        fields = [
            'user',
        ]

    def validate(self, data):
        user = self.context['request'].user
        review_id = self.context['view'].kwargs.get('review_id')

        if ReviewLike.objects.filter(user=user, review_id=review_id).exists():
            raise serializers.ValidationError({
                'detail': 'You have already liked this review.'
            })
        return data
    
    def create(self, validated_data):
        user = self.context['request'].user
        review_id = self.context['view'].kwargs.get('review_id')
        review = get_object_or_404(Review, id=review_id)
        return ReviewLike.objects.create(user=user, review=review)