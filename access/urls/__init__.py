from django.urls import include, path

urlpatterns = [
    path("menu/", include("access.urls.menu")),
    path("action/", include("access.urls.action")),
    path("event/", include("access.urls.event")),
    path("system/", include("access.urls.system")),
    path("role/", include("access.urls.role")),
    path("group/", include("access.urls.group")),
    path("permission/", include("access.urls.permission")),
    path("user-role/", include("access.urls.user_role")),
    path("user-group/", include("access.urls.user_group")),
    path("user-group-role/", include("access.urls.user_group_role")),
    path("permission-role/", include("access.urls.permission_role")),
    path("permission-system/", include("access.urls.permission_system")),
    path("role-menu/", include("access.urls.role_menu")),
]
