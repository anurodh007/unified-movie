from rest_framework import viewsets

from movies.models import Genre
from movies.serializers.genre_serializer import GenreSerializer


class GenreViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    lookup_field = 'tmdb_id'