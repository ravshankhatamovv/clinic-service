from django.urls import path
from .views import (
    UserMeAPIView,
    MyTokenObtainPairView,
    MyTokenRefreshView,
    UserUpdateViewSet, SendOTPView,
)

urlpatterns = [
    path('update/<int:pk>/', UserUpdateViewSet.as_view(), name='user-update'),

    path('token/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),  # Login
    path('token/refresh/', MyTokenRefreshView.as_view(), name='token_refresh'),  # Refresh token
    path('send-otp/', SendOTPView.as_view(), name='send_otp'),  # Refresh token
    path('me/', UserMeAPIView.as_view(), name='user-me'),
]
