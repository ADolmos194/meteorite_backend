from audit.utils import EVENT_ANNUL
from config.base_views import BaseViewFactory
from ..models import UserRole
from ..serializers import UserRoleSerializer

factory = BaseViewFactory(UserRole, UserRoleSerializer, "usuario-rol", "access_user_role")

user_role_get_view = factory.get_view(filters=["user_id", "role_id"])
user_role_assign_view = factory.bulk_assign_view("user_id", "role")
user_role_remove_view = factory.status_change_view("DELETE", EVENT_ANNUL)
