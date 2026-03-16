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