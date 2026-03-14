from rest_framework import viewsets, generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.pagination import PageNumberPagination

from django_filters.rest_framework import DjangoFilterBackend

from movies.models import Genre, Movie, StreamingPlatform
from movies.serializers.genre_serializer import GenreSerializer
from movies.serializers.movie_serializer import MovieListSerializer, MovieDetailSerializer
from movies.serializers.streaming_platform_serializer import StreamingPlatformSerializer
from movies.services.movie_service import (
    get_or_create_movie,
    search_movies,
    get_streaming_platforms,
    get_trending_movies
)
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

        if results is None or not results:
            return Response(
                {'detail': f'Movies containing "{search_query}" not found.'},
                status=status.HTTP_404_NOT_FOUND
            )
        if hasattr(results, 'order_by'):
            results = self.filter_queryset(results)
            if not results.query.order_by:
                results = results.order_by('-popularity')
        
        page = self.paginate_queryset(results)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(results, many=True)
        return Response(serializer.data)
    
    def retrieve(self, request, *args, **kwargs):
        tmdb_id = kwargs.get('tmdb_id')
        movie = get_or_create_movie(tmdb_id)
        if movie is None:
            return Response(
                {'detail': f'Movie with TMDB ID {tmdb_id} not found or API unavailable.'},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = self.get_serializer(movie)
        return Response(serializer.data)
    

"""
ViewSet to list and retrieve streaming platforms
"""
class StreamingPlatformViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = StreamingPlatform.objects.order_by('tmdb_id')
    serializer_class = StreamingPlatformSerializer
    lookup_field = 'tmdb_id'


"""
APIView to list where the movie is streaming
"""
class StreamingListAPIView(generics.ListAPIView):
    queryset = StreamingPlatform.objects.all()
    serializer_class = StreamingPlatformSerializer

    def list(self, request, *args, **kwargs):
        tmdb_id = kwargs.get('tmdb_id')
        platforms = get_streaming_platforms(tmdb_id)

        if platforms is None:
            return Response(
                {'detail': f'Movie providers for movie {tmdb_id} not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        platforms = platforms.order_by('tmdb_id')

        page = self.paginate_queryset(platforms)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(platforms, many=True)
        return Response(serializer.data)
    

"""
APIView to list trending movies (day)
"""
class TrendingMoviesAPIView(APIView):
    def get(self, request):
        page_num = request.query_params.get('page', 1)
        movies = get_trending_movies(page_num)
        if movies is None:
            return Response(
                {'details': 'Error 404: Not Found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        paginator = PageNumberPagination()
        results_page = paginator.paginate_queryset(movies, request, view=self)
        serializer = MovieListSerializer(results_page, many=True, context={'request': request})
        return paginator.get_paginated_response(serializer.data)