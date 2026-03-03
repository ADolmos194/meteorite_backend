from django.urls import path
from access.views.action import (
    action_get_view,
    action_select_view,
    action_create_view,
    action_update_view,
    action_inactivate_view,
    action_restore_view,
    action_annul_view,
)

urlpatterns = [
    path("get/", action_get_view, name="action-get"),
    path("select/", action_select_view, name="action-select"),
    path("create/", action_create_view, name="action-create"),
    path("update/", action_update_view, name="action-update"),
    path("inactivate/", action_inactivate_view, name="action-inactivate"),
    path("restore/", action_restore_view, name="action-restore"),
    path("annul/", action_annul_view, name="action-annul"),
]
