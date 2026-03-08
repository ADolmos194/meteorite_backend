from audit.utils import EVENT_ANNUL
from config.base_views import BaseViewFactory
from ..models import UserGroup
from ..serializers import UserGroupSerializer

factory = BaseViewFactory(UserGroup, UserGroupSerializer, "usuario-grupo", "access_user_group")

user_group_get_view = factory.get_view(filters=["user_id", "group_id"])
user_group_assign_view = factory.bulk_assign_view("user_id", "group")
user_group_remove_view = factory.status_change_view("DELETE", EVENT_ANNUL)
