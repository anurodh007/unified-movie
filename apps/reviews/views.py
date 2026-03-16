from django.shortcuts import get_object_or_404
from django.db.utils import IntegrityError

from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from reviews.models import Review
from reviews.serializers.review_serializer import ReviewSerializer

from movies.models import Movie

from core.permissions import IsOwnerOrReadOnly


"""
Movie-Reviews List and Create API View
"""
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

    def create(self, request, *args, **kwargs):
        try:
            return super().create(request, *args, **kwargs)
        except IntegrityError:
            return Response(
                {'detail': 'Only one review per user per movie is allowed.'},
                status=status.HTTP_400_BAD_REQUEST
            )


"""
API View for Movie Review-Details
"""
class ReviewDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Review.objects.select_related('user', 'movie')
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]

    def get_queryset(self):
        tmdb_id = self.kwargs.get('tmdb_id')
        return self.queryset.filter(movie__tmdb_id=tmdb_id)


"""
User Reviews List API View
"""
class UserReviewListAPIView(generics.ListAPIView):
    queryset = Review.objects.select_related('user', 'movie').order_by('-created_at')
    serializer_class = ReviewSerializer

    def get_queryset(self):
        username = self.kwargs.get('username')
        return self.queryset.filter(user__username=username)