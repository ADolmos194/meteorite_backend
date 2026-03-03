from django.urls import path
from access.views.group import (
    group_get_view,
    group_select_view,
    group_create_view,
    group_update_view,
    group_inactivate_view,
    group_restore_view,
    group_annul_view,
)

urlpatterns = [
    path("get/", group_get_view, name="group-get"),
    path("select/", group_select_view, name="group-select"),
    path("create/", group_create_view, name="group-create"),
    path("update/", group_update_view, name="group-update"),
    path("inactivate/", group_inactivate_view, name="group-inactivate"),
    path("restore/", group_restore_view, name="group-restore"),
    path("annul/", group_annul_view, name="group-annul"),
]
