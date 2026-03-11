from rest_framework import generics
from rest_framework.permissions import AllowAny

from users.models import User
from users.serializers.register_serializer import UserRegisterSerializer
from users.serializers.user_serializer import OwnerUserSerializer, PublicUserSerializer
from users.permissions import IsOwnerOrReadOnly


class UserRegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegisterSerializer
    permission_classes = [AllowAny]


class UserDetailView(generics.RetrieveUpdateAPIView):
    queryset = User.objects.all()
    serializer_class = PublicUserSerializer
    lookup_field = 'username'
    permission_classes = [IsOwnerOrReadOnly]

    def get_serializer_class(self):
        user = self.request.user
        if user.is_authenticated and (user.username == self.kwargs.get('username')):
            return OwnerUserSerializer
        return super().get_serializer_class()