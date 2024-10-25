from django.urls import path
from .views import UserRegistrationView

urlpatterns = [
    # path("jwt/", views.auth),
    path("register/", UserRegistrationView.as_view(), name='user-register')
]