from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.reverse import reverse
from reviews.models import Review, ReviewComment, ReviewLike


class CommentSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.SerializerMethodField()
    user = serializers.ReadOnlyField(source='user.username')

    class Meta:
        model = ReviewComment
        fields = [
            'url',
            'id',
            'user',
            'comment_text',
            'created_at'
        ]

    def get_url(self, obj):
        request = self.context.get('request')
        return reverse(
            viewname='reviews:comment-detail',
            kwargs={
                'tmdb_id': obj.review.movie.tmdb_id,
                'review_id': obj.review_id,
                'comment_id': obj.pk
            },
            request=request
        )


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