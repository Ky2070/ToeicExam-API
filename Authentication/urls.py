from django.urls import path
from .views import *
from rest_framework_simplejwt.views import TokenRefreshSlidingView, TokenRefreshView, TokenObtainSlidingView

urlpatterns = [
    # path("jwt/", views.auth),
    path("register/", UserRegistrationView.as_view(), name='user-register'),
    path('login/', UserLoginView.as_view(), name='token_obtain'),
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/', TokenObtainSlidingView.as_view(), name='token_obtain'),
    path('token/refresh/', TokenRefreshSlidingView.as_view(), name='token_refresh'),
    path('user/', UserProfileView.as_view(), name='user_profile'),
    path('users/all/', UserAllView.as_view(), name='user_all'),
]
