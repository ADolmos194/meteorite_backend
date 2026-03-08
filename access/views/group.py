from config.base_views import BaseViewFactory
from config.utils import STATUS_ACTIVO, STATUS_INACTIVO, STATUS_ANULADO
from audit.utils import EVENT_RESTORE, EVENT_INACTIVATE, EVENT_ANNUL
from ..models import Group
from ..serializers import GroupSerializer

factory = BaseViewFactory(Group, GroupSerializer, "grupos", "access_group")

group_get_view = factory.get_view()
group_select_view = factory.select_view()
group_create_view = factory.create_view(unique_fields=["name"])
group_update_view = factory.update_view(unique_fields=["name"])
group_inactivate_view = factory.status_change_view(STATUS_INACTIVO, EVENT_INACTIVATE)
group_restore_view = factory.status_change_view(STATUS_ACTIVO, EVENT_RESTORE)
group_annul_view = factory.status_change_view(STATUS_ANULADO, EVENT_ANNUL)
