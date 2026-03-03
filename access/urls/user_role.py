from django.urls import path
from access.views.user_role import (
    user_role_get_view,
    user_role_assign_view,
    user_role_remove_view,
)

urlpatterns = [
    path("get/", user_role_get_view, name="user-role-get"),
    path("assign/", user_role_assign_view, name="user-role-assign"),
    path("remove/", user_role_remove_view, name="user-role-remove"),
]
