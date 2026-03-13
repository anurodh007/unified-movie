from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.filters import SearchFilter, OrderingFilter

from django_filters.rest_framework import DjangoFilterBackend

from movies.models import Genre, Movie
from movies.serializers.genre_serializer import GenreSerializer
from movies.serializers.movie_serializer import MovieListSerializer, MovieDetailSerializer
from movies.services.movie_service import get_or_create_movie, search_movies
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
    filter_backends = [
        DjangoFilterBackend,
        OrderingFilter
    ]
    filterset_class = MovieFilter
    ordering_fields = ['release_date', 'average_rating']

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return MovieDetailSerializer
        return super().get_serializer_class()
    
    def list(self, request, *args, **kwargs):
        search_query = request.query_params.get('search', '')
        results = search_movies(search_query)

        if hasattr(results, 'order_by'):
            results = self.filter_queryset(results)
        
        page = self.paginate_queryset(results)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(results, many=True)
        return Response(serializer.data)
    
    def retrieve(self, request, tmdb_id=None):
        movie = get_or_create_movie(tmdb_id)
        serializer = self.get_serializer(movie)
        return Response(serializer.data)