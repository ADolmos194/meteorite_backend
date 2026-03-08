from audit.utils import EVENT_ANNUL, EVENT_INACTIVATE, EVENT_RESTORE
from config.base_views import BaseViewFactory
from config.utils import STATUS_ACTIVO, STATUS_INACTIVO, STATUS_ANULADO
from ..models import Event
from ..serializers import EventSerializer

factory = BaseViewFactory(Event, EventSerializer, "evento", "access_event")

event_get_view = factory.get_view()
event_select_view = factory.select_view()
event_create_view = factory.create_view(unique_fields=["name"])
event_update_view = factory.update_view(unique_fields=["name"])
event_inactivate_view = factory.status_change_view(STATUS_INACTIVO, EVENT_INACTIVATE)
event_restore_view = factory.status_change_view(STATUS_ACTIVO, EVENT_RESTORE)
event_annul_view = factory.status_change_view(STATUS_ANULADO, EVENT_ANNUL)
