from rest_framework import serializers
from reviews.models import Review


class ReviewSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')
    movie = serializers.ReadOnlyField(source='movie.title')

    class Meta:
        model = Review
        fields = [
            'id',
            'user',
            'movie',
            'review_text',
            'rating',
            'created_at'
        ]

    def validate_rating(self, value):
        if not (1 <= value <= 10):
            raise serializers.ValidationError({
                'rating': 'Rating must be between 1 and 10.'
            })
        return value
    
    def validate(self, data):
        user = self.context['request'].user
        tmdb_id = self.context['view'].kwargs.get('tmdb_id')
        existing_review = Review.objects.filter(user=user, movie__tmdb_id=tmdb_id)

        if self.instance:
            existing_review = existing_review.exclude(pk=self.instance.pk)

        if existing_review.exists():
            raise serializers.ValidationError({
                'detail': 'You have already reviewed this movie.'
            })
        return data