from django.urls import path
from . import views

from rest_framework_simplejwt.views import (
    TokenObtainPairView, #Accepts user credentials (typically username and password) and returns a pair of tokens: an access token and a refresh token.
    TokenRefreshView, #Accepts a valid refresh token and returns a new access token.
    TokenVerifyView, #Accepts a token and verifies its validity.
)



urlpatterns = [
    path('register/', views.UserRegistrationView.as_view(), name='register'),
    path('login/', views.UserLoginView.as_view(), name='login'),

     # JWT token endpoints
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
]