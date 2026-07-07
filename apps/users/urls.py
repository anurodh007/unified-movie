from django.urls import path, include
from users import views

from reviews.views import (
    UserReviewListAPIView,
    UserCommentListAPIView,
    UserLikeListAPIView
)

from watchlist.views import UserWatchlistListAPIView


urlpatterns = [
    path('<str:username>/', views.UserDetailView.as_view(), name='user_detail'),

    # Endpoint for user watchlist
    path('<str:username>/watchlist/', UserWatchlistListAPIView.as_view(), name='user-watchlist-list'),

    # Endpoint for user reviews
    path('<str:username>/reviews/', UserReviewListAPIView.as_view(), name='user-reviews-list'),

    # Endpoint for user comments
    path('<str:username>/comments/', UserCommentListAPIView.as_view(), name='user-comments-list'),

    # Endpoint for user likes
    path('<str:username>/likes/', UserLikeListAPIView.as_view(), name='user-likes-list'),
]