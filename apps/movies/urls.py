from django.urls import path
from rest_framework.routers import DefaultRouter
from movies.views import (
    GenreViewSet,
    MovieViewSet,
    StreamingPlatformViewSet,
    StreamingListAPIView,
    TrendingMoviesAPIView
)

from reviews.views import (
    ReviewListCreateAPIView,
    ReviewDetailAPIView,
)


urlpatterns = [
    path('<tmdb_id>/streaming/', StreamingListAPIView.as_view(), name='movie-streaming'),
    path('trending/', TrendingMoviesAPIView.as_view(), name='trending-movies'),

    # Endpoints for movie reviews
    path('<tmdb_id>/reviews/', ReviewListCreateAPIView.as_view(), name='movie-reviews-list'),
    path('<tmdb_id>/reviews/<int:pk>/', ReviewDetailAPIView.as_view(), name='review-detail'),
]


router = DefaultRouter()
router.register('genres', GenreViewSet, basename='genre')
router.register('platforms', StreamingPlatformViewSet, basename='platform')
router.register('', MovieViewSet, basename='movie')

urlpatterns += router.urls