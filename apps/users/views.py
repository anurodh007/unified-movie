from rest_framework import generics

from users.models import User
from users.serializers.register_serializer import UserRegisterSerializer


class UserRegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegisterSerializer