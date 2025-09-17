from django.urls import path
from .views import *
from .sse_views import (
    sse_notifications,
    sse_test,
    sse_notifications_drf,
    sse_notifications_sync,
)

urlpatterns = [
    # path("jwt/", views.auth),
    path("register/", UserRegistrationView.as_view(), name="user-register"),
    path("login/", UserLoginView.as_view(), name="token_obtain"),
    path("refresh/", CustomTokenRefreshView.as_view(), name="token_refresh"),
    path("user/", UserProfileView.as_view(), name="user_profile"),
    path("users/all/", UserAllView.as_view(), name="user_all"),
    # SSE endpoints
    path("sse/notifications/", sse_notifications, name="sse_notifications"),
    path(
        "sse/notifications-sync/", sse_notifications_sync, name="sse_notifications_sync"
    ),  # Sync version for dev server
    path("sse/test/", sse_test, name="sse_test"),  # For testing SSE connectivity
    path(
        "sse/notifications-drf/", sse_notifications_drf, name="sse_notifications_drf"
    ),  # Alternative DRF version
]
