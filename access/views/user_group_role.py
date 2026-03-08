from audit.utils import EVENT_ANNUL
from config.base_views import BaseViewFactory
from ..models import UserGroupRole
from ..serializers import UserGroupRoleSerializer

factory = BaseViewFactory(UserGroupRole, UserGroupRoleSerializer, "usuario-grupo-rol", "access_user_group_role")

user_group_role_get_view = factory.get_view(filters=["user_id", "group_id"])
user_group_role_assign_view = factory.bulk_assign_view("user_id", "role", extra_fields=["group_id"])
user_group_role_remove_view = factory.status_change_view("DELETE", EVENT_ANNUL)
