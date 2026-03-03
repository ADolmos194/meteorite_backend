from django.urls import path
from access.views.role import (
    role_get_view,
    role_select_view,
    role_create_view,
    role_update_view,
    role_inactivate_view,
    role_restore_view,
    role_annul_view,
)

urlpatterns = [
    path("get/", role_get_view, name="role-get"),
    path("select/", role_select_view, name="role-select"),
    path("create/", role_create_view, name="role-create"),
    path("update/", role_update_view, name="role-update"),
    path("inactivate/", role_inactivate_view, name="role-inactivate"),
    path("restore/", role_restore_view, name="role-restore"),
    path("annul/", role_annul_view, name="role-annul"),
]
