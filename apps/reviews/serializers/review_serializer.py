from rest_framework import serializers
from rest_framework.reverse import reverse
from reviews.models import Review


class ReviewSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.SerializerMethodField()
    user = serializers.ReadOnlyField(source='user.username')
    movie = serializers.ReadOnlyField(source='movie.title')

    class Meta:
        model = Review
        fields = [
            'url',
            'id',
            'user',
            'movie',
            'review_text',
            'rating',
            'created_at'
        ]

    def get_url(self, obj):
        request = self.context.get('request')
        return reverse(
            viewname='reviews:review-detail',
            kwargs={
                'tmdb_id': obj.movie.tmdb_id,
                'review_id': obj.pk
            },
            request=request
        )

    def validate_rating(self, value):
        if not (1 <= value <= 10):
            raise serializers.ValidationError('Rating must be between 1 and 10.')
        return value
    
    def validate(self, data):
        request = self.context.get('request')
        if not request or not request.user:
            return data

        view = self.context.get('view')
        tmdb_id = view.kwargs.get('tmdb_id') if view else None

        if tmdb_id:
            existing_review = Review.objects.filter(user=request.user, movie__tmdb_id=tmdb_id)

            if self.instance:
                existing_review = existing_review.exclude(pk=self.instance.pk)

            if existing_review.exists():
                raise serializers.ValidationError({
                    'detail': 'You have already reviewed this movie.'
                })
            
        return data