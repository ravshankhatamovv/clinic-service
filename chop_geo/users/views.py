
from rest_framework import generics

from django.contrib.auth import get_user_model
from django.core.cache import cache
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from chop_geo.users.serializers import (
    UserMeSerializer,
    UserSerializer,
    CreateUserSerializer, UpdateUserSerializer, TokenObtainSerializer
)

User = get_user_model()



class UserMeAPIView(generics.RetrieveAPIView):
    serializer_class = UserMeSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

    def get(self, request, *args, **kwargs):
        user = self.get_object()
        serialized_user = UserSerializer(user).data
        data = {
            'user': serialized_user
        }
        return Response(data, status=status.HTTP_200_OK)


class UserUpdateViewSet(generics.UpdateAPIView):
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = UpdateUserSerializer

    def perform_update(self, serializer):
        serializer.save(updated_from=self.request.user if self.request.user.is_authenticated else None)


class MyTokenObtainPairView(TokenObtainPairView):
    permission_classes = (AllowAny,)
    serializer_class = TokenObtainSerializer

    def post(self, request, *args, **kwargs):  # noqa
        response = super().post(request, *args, **kwargs)
        if response.status_code == status.HTTP_200_OK:
            refresh_token = response.data.get('refresh')
            if refresh_token:
                # Cache the refresh token with a short expiry time
                cache.set(refresh_token, 'valid', timeout=60 * 60 * 24)  # 1 day
        return response


class MyTokenRefreshView(TokenRefreshView):
    permission_classes = (AllowAny,)


class SendOTPView(generics.CreateAPIView):
    serializer_class = CreateUserSerializer
    permission_classes = (AllowAny,)
