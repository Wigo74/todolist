from django.contrib.auth import login, logout
from rest_framework import permissions, status
from rest_framework.generics import (
    CreateAPIView,
    GenericAPIView,
    RetrieveUpdateDestroyAPIView,
    UpdateAPIView,
)
from rest_framework.response import Response

from core.models import User
from core.serializers import (
    CreateUserSerializer,
    LoginSerializer,
    UserSerializer,
    UpdatePasswordSerializer,
)


class SignupView(CreateAPIView):
    """ Вход для пользователя """
    model = User
    permission_classes = [permissions.AllowAny]
    serializer_class = CreateUserSerializer

    def perform_create(self, serializer):
        super().perform_create(serializer)
        login(
            self.request,
            user=serializer.user,
            backend="django.contrib.auth.backends.ModelBackend",
        )


class LoginView(GenericAPIView):
    """ Авторизация пользователя """
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        s: LoginSerializer = self.get_serializer(data=request.data)
        s.is_valid(raise_exception=True)
        user = s.validated_data["user"]
        login(request=request, user=user)
        user_serializer = UserSerializer(instance=user)
        return Response(user_serializer.data)


class ProfileView(RetrieveUpdateDestroyAPIView):
    """ Профиль пользователя """
    model = User
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user

    def delete(self, request, *args, **kwargs):
        logout(request)
        return Response({})


class UpdatePasswordView(UpdateAPIView):
    """ Редактирование пароля """
    model = User
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UpdatePasswordSerializer

    def get_object(self):
        return self.request.user
