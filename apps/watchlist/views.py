from rest_framework import generics
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated, AllowAny

from watchlist.models import Watchlist
from watchlist.serializers import WatchlistSerializer

from movies.services.movie_service import get_or_create_movie


"""
Watchlist List-Create API View
"""
class WatchlistListCreateAPIView(generics.ListCreateAPIView):
    queryset = Watchlist.objects.select_related('user', 'movie').order_by('-created_at')
    serializer_class = WatchlistSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        tmdb_id = serializer.validated_data.pop('tmdb_id')
        movie = get_or_create_movie(tmdb_id)
        serializer.save(user=self.request.user, movie=movie)


"""
Watchlist Delete A Movie API View
"""
class WatchlistDestroyAPIView(generics.DestroyAPIView):
    queryset = Watchlist.objects.select_related('user', 'movie')
    lookup_url_kwarg = 'tmdb_id'
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        return get_object_or_404(
            self.queryset,
            user=self.request.user,
            movie__tmdb_id=self.kwargs.get('tmdb_id')
        )
    

"""
User Watchlist List API View
"""
class UserWatchlistListAPIView(generics.ListAPIView):
    queryset = Watchlist.objects.select_related('user', 'movie').order_by('-created_at')
    serializer_class = WatchlistSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return self.queryset.filter(user__username=self.kwargs.get('username'))