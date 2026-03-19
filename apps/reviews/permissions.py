from django.shortcuts import get_object_or_404
from rest_framework import permissions
from reviews.models import Review


class IsOwnerOrReviewOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        
        return (obj.user == request.user) or (obj.review.user == request.user)
    

class IsNotReviewOwner(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        
        review_id = view.kwargs.get('review_id')
        review = get_object_or_404(Review, id=review_id)

        return review.user != request.user