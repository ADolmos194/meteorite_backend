from django.urls import path
from access.views.event import (
    event_get_view,
    event_select_view,
    event_create_view,
    event_update_view,
    event_inactivate_view,
    event_restore_view,
    event_annul_view,
)

urlpatterns = [
    path("get/", event_get_view, name="event-get"),
    path("select/", event_select_view, name="event-select"),
    path("create/", event_create_view, name="event-create"),
    path("update/", event_update_view, name="event-update"),
    path("inactivate/", event_inactivate_view, name="event-inactivate"),
    path("restore/", event_restore_view, name="event-restore"),
    path("annul/", event_annul_view, name="event-annul"),
]
