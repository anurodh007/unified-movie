from django.urls import path

from reviews.views import (
    ReviewListCreateAPIView,
    ReviewDetailAPIView,
    CommentListCreateAPIView,
    CommentDetailAPIView
)


urlpatterns = [
    # Endpoints for movie-reviews
    path('', ReviewListCreateAPIView.as_view(), name='movie-reviews-list'),
    path('<int:review_id>/', ReviewDetailAPIView.as_view(), name='review-detail'),

    # Endpoints for review comments
    path('<int:review_id>/comments/', CommentListCreateAPIView.as_view(), name='review-comments'),
    path('<int:review_id>/comments/<int:comment_id>/', CommentDetailAPIView.as_view(), name='comment-detail'),
]