from config.base_views import BaseViewFactory
from config.utils import STATUS_ACTIVO, STATUS_INACTIVO, STATUS_ANULADO
from audit.utils import EVENT_RESTORE, EVENT_INACTIVATE, EVENT_ANNUL
from ..models import Role
from ..serializers import RoleSerializer

factory = BaseViewFactory(Role, RoleSerializer, "roles", "access_role")

role_get_view = factory.get_view()
role_select_view = factory.select_view()
role_create_view = factory.create_view(unique_fields=["name"])
role_update_view = factory.update_view(unique_fields=["name"])
role_inactivate_view = factory.status_change_view(STATUS_INACTIVO, EVENT_INACTIVATE)
role_restore_view = factory.status_change_view(STATUS_ACTIVO, EVENT_RESTORE)
role_annul_view = factory.status_change_view(STATUS_ANULADO, EVENT_ANNUL)
