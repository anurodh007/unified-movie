from rest_framework import viewsets

from movies.models import Genre, Movie
from movies.serializers.genre_serializer import GenreSerializer
from movies.serializers.movie_serializer import MovieListSerializer, MovieDetailSerializer


class GenreViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    lookup_field = 'tmdb_id'
    pagination_class = None


class MovieViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Movie.objects.prefetch_related('genres').order_by('-popularity')
    serializer_class = MovieListSerializer
    lookup_field = 'tmdb_id'

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return MovieDetailSerializer
        return super().get_serializer_class()