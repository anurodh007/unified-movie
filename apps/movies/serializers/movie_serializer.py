from rest_framework import serializers

from movies.models import Movie


class MovieListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Movie
        fields = [
            'tmdb_id',
            'title',
            'popularity',
            'average_rating',
            'poster_path',
        ]


class MovieDetailSerializer(serializers.ModelSerializer):
    genres = serializers.SlugRelatedField(many=True, read_only=True, slug_field='name')

    class Meta:
        model = Movie
        fields = [
            'tmdb_id',
            'title',
            'overview',
            'release_date',
            'runtime',
            'popularity',
            'average_rating',
            'vote_count',
            'genres',
            'poster_path',
            'backdrop_path',
        ]