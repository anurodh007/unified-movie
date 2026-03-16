from django.urls import path
from users import views

from reviews.views import (
    UserReviewListAPIView
)


urlpatterns = [
    path('<str:username>/', views.UserDetailView.as_view(), name='user_detail'),

    # Endpoints for user reviews
    path('<str:username>/reviews/', UserReviewListAPIView.as_view(), name='user-reviews-list'),
]