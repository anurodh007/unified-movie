from django.urls import path
from .views import RecommendationAPIView, CollaborativeAPIView


urlpatterns = [
    path('content-based/', RecommendationAPIView.as_view(), name='content-recommendations'),
    path('collaborative/', CollaborativeAPIView.as_view(), name='collab-recommendations'),
]