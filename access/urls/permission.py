from django.urls import path
from access.views.permission import (
    permission_get_view,
    permission_select_view,
    permission_create_view,
    permission_update_view,
    permission_inactivate_view,
    permission_restore_view,
    permission_annul_view,
)

urlpatterns = [
    path("get/", permission_get_view, name="permission-get"),
    path("select/", permission_select_view, name="permission-select"),
    path("create/", permission_create_view, name="permission-create"),
    path("update/", permission_update_view, name="permission-update"),
    path(
        "inactivate/",
        permission_inactivate_view,
        name="permission-inactivate"),
    path("restore/", permission_restore_view, name="permission-restore"),
    path("annul/", permission_annul_view, name="permission-annul"),
]
