from audit.utils import EVENT_ANNUL, EVENT_INACTIVATE, EVENT_RESTORE
from config.base_views import BaseViewFactory
from config.utils import STATUS_ACTIVO, STATUS_INACTIVO, STATUS_ANULADO
from ..models import Action
from ..serializers import ActionSerializer

factory = BaseViewFactory(Action, ActionSerializer, "acción", "access_action")

action_get_view = factory.get_view()
action_select_view = factory.select_view()
action_create_view = factory.create_view(unique_fields=["name"])
action_update_view = factory.update_view(unique_fields=["name"])
action_inactivate_view = factory.status_change_view(STATUS_INACTIVO, EVENT_INACTIVATE)
action_restore_view = factory.status_change_view(STATUS_ACTIVO, EVENT_RESTORE)
action_annul_view = factory.status_change_view(STATUS_ANULADO, EVENT_ANNUL)
