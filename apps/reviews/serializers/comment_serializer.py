from rest_framework import serializers
from reviews.models import ReviewComment


class CommentSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')

    class Meta:
        model = ReviewComment
        fields = [
            'id',
            'user',
            'comment_text',
            'created_at'
        ]