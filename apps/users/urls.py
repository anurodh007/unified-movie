from django.urls import path, include
from users import views

from reviews.views import (
    UserReviewListAPIView,
    UserCommentListAPIView
)


urlpatterns = [
    path('<str:username>/', views.UserDetailView.as_view(), name='user_detail'),

    # Endpoints for user reviews
    path('<str:username>/reviews/', UserReviewListAPIView.as_view(), name='user-reviews-list'),

    # Endpoint for user comments
    path('<str:username>/comments/', UserCommentListAPIView.as_view(), name='user-comments-list'),
]