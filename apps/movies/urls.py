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
    CommentListCreateAPIView
)


urlpatterns = [
    path('<tmdb_id>/streaming/', StreamingListAPIView.as_view(), name='movie-streaming'),
    path('trending/', TrendingMoviesAPIView.as_view(), name='trending-movies'),

    # Endpoints for movie reviews
    path('<tmdb_id>/reviews/', ReviewListCreateAPIView.as_view(), name='movie-reviews-list'),
    path('<tmdb_id>/reviews/<int:review_id>/', ReviewDetailAPIView.as_view(), name='review-detail'),

    # Endpoints for review comments
    path('<tmdb_id>/reviews/<int:review_id>/comments/', CommentListCreateAPIView.as_view(), name='review-comments'),
]


router = DefaultRouter()
router.register('genres', GenreViewSet, basename='genre')
router.register('platforms', StreamingPlatformViewSet, basename='platform')
router.register('', MovieViewSet, basename='movie')

urlpatterns += router.urls