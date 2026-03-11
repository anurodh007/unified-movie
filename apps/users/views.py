from rest_framework import generics
from rest_framework.permissions import AllowAny

from users.models import User
from users.serializers.register_serializer import UserRegisterSerializer
from users.serializers.user_serializer import UserSerializer


class UserRegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegisterSerializer
    permission_classes = [AllowAny]


class UserDetailView(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_field = 'username'
    permission_classes = [AllowAny]