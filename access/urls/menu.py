from django.urls import path
from access.views.menu import (
    menu_get_view,
    menu_select_view,
    menu_tree_view,
    menu_create_view,
    menu_update_view,
    menu_inactivate_view,
    menu_restore_view,
    menu_annul_view,
)

urlpatterns = [
    path("get/", menu_get_view, name="menu-get"),
    path("select/", menu_select_view, name="menu-select"),
    path("tree/", menu_tree_view, name="menu-tree"),
    path("create/", menu_create_view, name="menu-create"),
    path("update/", menu_update_view, name="menu-update"),
    path("inactivate/", menu_inactivate_view, name="menu-inactivate"),
    path("restore/", menu_restore_view, name="menu-restore"),
    path("annul/", menu_annul_view, name="menu-annul"),
]
