from django.urls import path
from access.views.user_group_role import (
    user_group_role_get_view,
    user_group_role_assign_view,
    user_group_role_remove_view,
)

urlpatterns = [
    path("get/", user_group_role_get_view, name="user-group-role-get"),
    path(
        "assign/",
        user_group_role_assign_view,
        name="user-group-role-assign"),
    path(
        "remove/",
        user_group_role_remove_view,
        name="user-group-role-remove"),
]
