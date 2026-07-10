from rest_framework import serializers
from movies.serializers.fields import TMDBImageField


class RecommendationSerializer(serializers.Serializer):
    tmdb_id = serializers.IntegerField()
    title = serializers.CharField(source='movie.title')
    average_rating = serializers.FloatField(source='movie.average_rating')
    poster_path = TMDBImageField(source='movie.poster_path')
    score = serializers.FloatField()
    recommendation_type = serializers.CharField()