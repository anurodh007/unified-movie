from rest_framework import serializers
from movies.models import Genre


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = [
            'id',
            'tmdb_id',
            'name',
        ]