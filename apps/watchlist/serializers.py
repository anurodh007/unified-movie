from rest_framework import serializers
from watchlist.models import Watchlist
from movies.serializers.movie_serializer import MovieListSerializer


class WatchlistSerializer(serializers.ModelSerializer):
    movie = MovieListSerializer(read_only=True)
    tmdb_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Watchlist
        fields = [
            'id',
            'movie',
            'tmdb_id',
            'created_at',
        ]
        read_only_fields = [
            'id',
            'created_at',
        ]