from django.urls import path
from rest_framework.routers import DefaultRouter
from movies.views import GenreViewSet, MovieViewSet


urlpatterns = []


router = DefaultRouter()
router.register('genres', GenreViewSet, basename='genre')
router.register('', MovieViewSet, basename='movie')

urlpatterns += router.urls