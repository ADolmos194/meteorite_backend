from audit.utils import EVENT_ANNUL
from config.base_views import BaseViewFactory
from ..models import PermissionSystem
from ..serializers import PermissionSystemSerializer

factory = BaseViewFactory(PermissionSystem, PermissionSystemSerializer, "permiso-sistema", "access_permission_system")

permission_system_get_view = factory.get_view(filters=["system_id", "permission_id"])
permission_system_assign_view = factory.bulk_assign_view("system_id", "permission")
permission_system_remove_view = factory.status_change_view("DELETE", EVENT_ANNUL)
