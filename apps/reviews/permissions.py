from rest_framework import permissions


class IsOwnerOrReviewOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        
        return (obj.user == request.user) or (obj.review.user == request.user) 