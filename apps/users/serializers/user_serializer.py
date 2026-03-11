from rest_framework import serializers
from users.models import User


class OwnerUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'first_name', 
            'last_name',
            'email',
            'bio',
            'profile_picture',
        ]
        extra_kwargs = {
            'username': {'read_only': True},
            'profile_picture': {'required': False, 'allow_null': True},
        }


class PublicUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'first_name', 
            'last_name',
            'bio',
            'profile_picture',
        ]