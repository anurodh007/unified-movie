from django.shortcuts import get_object_or_404

from rest_framework import generics
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from reviews.models import Review
from reviews.serializers.review_serializer import ReviewSerializer

from movies.models import Movie

from core.permissions import IsOwnerOrReadOnly


class ReviewListCreateAPIView(generics.ListCreateAPIView):
    queryset = Review.objects.select_related('user', 'movie').order_by('-created_at')
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        tmdb_id = self.kwargs.get('tmdb_id')
        return self.queryset.filter(movie__tmdb_id=tmdb_id)
    
    def perform_create(self, serializer):
        tmdb_id = self.kwargs.get('tmdb_id')
        movie = get_object_or_404(Movie, tmdb_id=tmdb_id)
        serializer.save(user=self.request.user, movie=movie)


class ReviewDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Review.objects.select_related('user', 'movie')
    serializer_class = ReviewSerializer
    permission_classes = [IsOwnerOrReadOnly]