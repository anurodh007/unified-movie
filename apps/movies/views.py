from rest_framework import viewsets
from rest_framework.response import Response

from movies.models import Genre, Movie
from movies.serializers.genre_serializer import GenreSerializer
from movies.serializers.movie_serializer import MovieListSerializer, MovieDetailSerializer
from movies.services.movie_service import get_or_create_movie
from movies.filters import MovieFilter


class GenreViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    lookup_field = 'tmdb_id'
    pagination_class = None


class MovieViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Movie.objects.prefetch_related('genres').order_by('-popularity')
    serializer_class = MovieListSerializer
    lookup_field = 'tmdb_id'
    filterset_class = MovieFilter

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return MovieDetailSerializer
        return super().get_serializer_class()
    
    def retrieve(self, request, tmdb_id=None):
        movie = get_or_create_movie(tmdb_id)
        serializer = self.get_serializer(movie)
        return Response(serializer.data)