from config.base_views import BaseViewFactory
from config.utils import STATUS_ACTIVO, STATUS_INACTIVO, STATUS_ANULADO
from audit.utils import EVENT_RESTORE, EVENT_INACTIVATE, EVENT_ANNUL
from ..models import Permission
from ..serializers import PermissionSerializer

factory = BaseViewFactory(Permission, PermissionSerializer, "permisos", "access_permission")

permission_get_view = factory.get_view()
permission_select_view = factory.select_view()
permission_create_view = factory.create_view(unique_fields=["decorator_name"])
permission_update_view = factory.update_view(unique_fields=["decorator_name"])
permission_inactivate_view = factory.status_change_view(STATUS_INACTIVO, EVENT_INACTIVATE)
permission_restore_view = factory.status_change_view(STATUS_ACTIVO, EVENT_RESTORE)
permission_annul_view = factory.status_change_view(STATUS_ANULADO, EVENT_ANNUL)
