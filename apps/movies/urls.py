from django.urls import path, include
from rest_framework.routers import DefaultRouter
from movies.views import (
    GenreViewSet,
    MovieViewSet,
    StreamingPlatformViewSet,
    StreamingListAPIView,
    TrendingMoviesAPIView
)


urlpatterns = [
    path('<tmdb_id>/streaming/', StreamingListAPIView.as_view(), name='movie-streaming'),
    path('trending/', TrendingMoviesAPIView.as_view(), name='trending-movies'),

    # Endpoints for movie reviews
    path('<tmdb_id>/reviews/', include('reviews.urls', namespace='reviews')),
]


router = DefaultRouter()
router.register('genres', GenreViewSet, basename='genre')
router.register('platforms', StreamingPlatformViewSet, basename='platform')
router.register('', MovieViewSet, basename='movie')

urlpatterns += router.urls