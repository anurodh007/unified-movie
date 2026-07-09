from rest_framework import serializers
from movies.serializers.fields import TMDBImageField


class RecommendationSerializer(serializers.Serializer):
    tmdb_id = serializers.IntegerField()
    title = serializers.CharField(source='movie.title')
    similarity_score = serializers.FloatField(source='score')
    average_rating = serializers.FloatField(source='movie.average_rating')
    poster_path = TMDBImageField(source='movie.poster_path')