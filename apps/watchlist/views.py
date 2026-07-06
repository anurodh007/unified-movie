from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from watchlist.models import Watchlist
from watchlist.serializers import WatchlistSerializer

from movies.services.movie_service import get_or_create_movie


"""
Watchlist List-Create API View
"""
class WatchlistListCreateAPIView(generics.ListCreateAPIView):
    queryset = Watchlist.objects.select_related('user', 'movie')
    serializer_class = WatchlistSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        tmdb_id = serializer.validated_data.pop('tmdb_id')
        movie = get_or_create_movie(tmdb_id)
        serializer.save(user=self.request.user, movie=movie)