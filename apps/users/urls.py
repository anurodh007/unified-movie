from django.urls import path, include
from users import views

from reviews.views import (
    UserReviewListAPIView,
    UserReviewDetailAPIView
)


urlpatterns = [
    path('<str:username>/', views.UserDetailView.as_view(), name='user_detail'),

    # Endpoints for user reviews
    path('<str:username>/reviews/', UserReviewListAPIView.as_view(), name='user-reviews-list'),
    path('<str:username>/reviews/<int:review_id>/', UserReviewDetailAPIView.as_view()),
]