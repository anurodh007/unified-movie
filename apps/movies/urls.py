from django.urls import path
from rest_framework.routers import DefaultRouter
from movies.views import GenreViewSet


urlpatterns = []


router = DefaultRouter()
router.register('genres', GenreViewSet, basename='genre')

urlpatterns += router.urls