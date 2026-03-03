from django.urls import path

from .views import (
    login_view,
    logout_view,
    register_view,
    resend_code_view,
    session_view,
    user_get_view,
    user_select_view,
    verify_code_view,
)

urlpatterns = [
    path("register/", register_view, name="register"),
    path("verify/", verify_code_view, name="verify"),
    path("resend/", resend_code_view, name="resend-code"),
    path("login/", login_view, name="login"),
    path("logout/", logout_view, name="logout"),
    path("session/", session_view, name="session"),
    path("user/get/", user_get_view, name="user-get"),
    path("user/select/", user_select_view, name="user-select"),
]
