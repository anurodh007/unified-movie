from django.urls import path
from rest_framework.routers import DefaultRouter
from movies.views import (
    GenreViewSet,
    MovieViewSet,
    StreamingPlatformViewSet,
    StreamingListAPIView
)


urlpatterns = [
    path('<tmdb_id>/streaming/', StreamingListAPIView.as_view(), name='movie-streaming'),
]


router = DefaultRouter()
router.register('genres', GenreViewSet, basename='genre')
router.register('platforms', StreamingPlatformViewSet, basename='platform')
router.register('', MovieViewSet, basename='movie')

urlpatterns += router.urls