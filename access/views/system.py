from config.base_views import BaseViewFactory
from config.utils import STATUS_ACTIVO, STATUS_INACTIVO, STATUS_ANULADO
from audit.utils import EVENT_RESTORE, EVENT_INACTIVATE, EVENT_ANNUL
from ..models import System
from ..serializers import SystemSerializer

factory = BaseViewFactory(System, SystemSerializer, "sistemas", "access_system")

system_get_view = factory.get_view()
system_select_view = factory.select_view()
system_create_view = factory.create_view(unique_fields=["name"])
system_update_view = factory.update_view(unique_fields=["name"])
system_inactivate_view = factory.status_change_view(STATUS_INACTIVO, EVENT_INACTIVATE)
system_restore_view = factory.status_change_view(STATUS_ACTIVO, EVENT_RESTORE)
system_annul_view = factory.status_change_view(STATUS_ANULADO, EVENT_ANNUL)
