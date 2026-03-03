from django.urls import path
from access.views.user_group import (
    user_group_get_view,
    user_group_assign_view,
    user_group_remove_view,
)

urlpatterns = [
    path("get/", user_group_get_view, name="user-group-get"),
    path("assign/", user_group_assign_view, name="user-group-assign"),
    path("remove/", user_group_remove_view, name="user-group-remove"),
]
