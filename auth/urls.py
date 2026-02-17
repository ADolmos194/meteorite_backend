from django.urls import path

from .views import (
    login_view,
    logout_view,
    register_view,
    session_view,
    verify_code_view,
)

urlpatterns = [
    path("register/", register_view, name="register"),
    path("verify/", verify_code_view, name="verify"),
    path("login/", login_view, name="login"),
    path("logout/", logout_view, name="logout"),
    path("session/", session_view, name="session"),
]
