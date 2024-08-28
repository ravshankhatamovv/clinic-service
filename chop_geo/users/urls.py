from django.urls import path
from .views import (
    UserMeAPIView,
    MyTokenObtainPairView,
    MyTokenRefreshView,
    MyTokenVerifyView,

    PasswordResetRequestAPIView,
    ConfirmOTPAPIView,
    ChangePasswordAPIView,
    UserCreateViewSet,
    UserUpdateViewSet,
)

urlpatterns = [
    path('register/', UserCreateViewSet.as_view(), name='create'),
    path('update/<int:pk>/', UserUpdateViewSet.as_view(), name='user-update'),

    path('token/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),  # Login
    path('token/refresh/', MyTokenRefreshView.as_view(), name='token_refresh'),  # Refresh token
    path('token/verify/', MyTokenVerifyView.as_view(), name='token_verify'),  # Verify token
    path('reset-password-request/', PasswordResetRequestAPIView.as_view(), name='reset-password'),
    path('confirm-otp/', ConfirmOTPAPIView.as_view(), name='confirm-otp'),  # Verify token
    path('change-password/', ChangePasswordAPIView.as_view(), name='change-password'),  # Verify token
    path('me/', UserMeAPIView.as_view(), name='user-me'),
]
