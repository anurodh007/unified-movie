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
        if not request or not obj.review or not obj.review.movie:
            return None

        return reverse(
            viewname='reviews:comment-detail',
            kwargs={
                'tmdb_id': obj.review.movie.tmdb_id,
                'review_id': obj.review_id,
                'comment_id': obj.pk
            },
            request=request
        )
    

class UserCommentSerializer(CommentSerializer):
    movie_title = serializers.ReadOnlyField(source='review.movie.title')
    movie_id = serializers.ReadOnlyField(source='review.movie.tmdb_id')
    review_id = serializers.ReadOnlyField(source='review.id')

    class Meta(CommentSerializer.Meta):
        fields = CommentSerializer.Meta.fields + [
            'movie_title',
            'movie_id',
            'review_id'
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
    

class UserLikeSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.SerializerMethodField()
    movie_id = serializers.ReadOnlyField(source='review.movie.tmdb_id')
    movie_title = serializers.ReadOnlyField(source='review.movie.title')
    review_id = serializers.ReadOnlyField(source='review.id')
    review_text = serializers.ReadOnlyField(source='review.review_text')

    class Meta:
        model = ReviewLike
        fields = [
            'url',
            'movie_id',
            'movie_title',
            'review_id',
            'review_text',
        ]

    def get_url(self, obj):
        request = self.context.get('request')
        if not request:
            return None
        
        return reverse(
            viewname='reviews:review-likes',
            kwargs={
                'tmdb_id': obj.review.movie.tmdb_id,
                'review_id': obj.review_id
            },
            request=request
        )