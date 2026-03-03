from django.urls import path
from access.views.role_menu import (
    role_menu_get_view,
    role_menu_assign_view,
    role_menu_remove_view,
)

urlpatterns = [
    path("get/", role_menu_get_view, name="role-menu-get"),
    path("assign/", role_menu_assign_view, name="role-menu-assign"),
    path("remove/", role_menu_remove_view, name="role-menu-remove"),
]
