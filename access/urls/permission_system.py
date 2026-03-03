from django.urls import path
from access.views.permission_system import (
    permission_system_get_view,
    permission_system_assign_view,
    permission_system_remove_view,
)

urlpatterns = [
    path(
        "get/",
        permission_system_get_view,
        name="permission-system-get"),
    path(
        "assign/",
        permission_system_assign_view,
        name="permission-system-assign"),
    path(
        "remove/",
        permission_system_remove_view,
        name="permission-system-remove"),
]
