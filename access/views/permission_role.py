from audit.utils import EVENT_ANNUL
from config.base_views import BaseViewFactory
from ..models import PermissionRole
from ..serializers import PermissionRoleSerializer

factory = BaseViewFactory(PermissionRole, PermissionRoleSerializer, "permiso-rol", "access_permission_role")

permission_role_get_view = factory.get_view(filters=["role_id", "permission_id"])
permission_role_assign_view = factory.bulk_assign_view("role_id", "permission")
permission_role_remove_view = factory.status_change_view("DELETE", EVENT_ANNUL)
