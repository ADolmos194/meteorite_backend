from django.urls import path
from access.views.system import (
    system_get_view,
    system_select_view,
    system_create_view,
    system_update_view,
    system_inactivate_view,
    system_restore_view,
    system_annul_view,
)

urlpatterns = [
    path("get/", system_get_view, name="system-get"),
    path("select/", system_select_view, name="system-select"),
    path("create/", system_create_view, name="system-create"),
    path("update/", system_update_view, name="system-update"),
    path("inactivate/", system_inactivate_view, name="system-inactivate"),
    path("restore/", system_restore_view, name="system-restore"),
    path("annul/", system_annul_view, name="system-annul"),
]
