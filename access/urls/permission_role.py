from django.urls import path
from access.views.permission_role import (
    permission_role_get_view,
    permission_role_assign_view,
    permission_role_remove_view,
)

urlpatterns = [
    path("get/", permission_role_get_view, name="permission-role-get"),
    path(
        "assign/",
        permission_role_assign_view,
        name="permission-role-assign"),
    path(
        "remove/",
        permission_role_remove_view,
        name="permission-role-remove"),
]
