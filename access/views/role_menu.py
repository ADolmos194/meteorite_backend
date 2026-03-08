from audit.utils import EVENT_ANNUL
from config.base_views import BaseViewFactory
from ..models import RoleMenu
from ..serializers import RoleMenuSerializer

factory = BaseViewFactory(RoleMenu, RoleMenuSerializer, "rol-menú", "access_role_menu")

role_menu_get_view = factory.get_view(filters=["role_id", "menu_id"], order_by=["menu__ordering", "menu__title"])
role_menu_assign_view = factory.bulk_assign_view("role_id", "menu")
role_menu_remove_view = factory.status_change_view("DELETE", EVENT_ANNUL)
