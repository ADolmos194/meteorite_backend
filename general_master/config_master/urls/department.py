from django.urls import path
from ..views.department import (
    department_get_view,
    department_create_view,
    department_update_view,
    department_inactivate_view,
    department_restore_view,
    department_annul_view,
    department_export_view,
    department_template_view,
    department_import_view,
    department_log_view,
    department_log_detail_view,
)

urlpatterns = [
    path("get/", department_get_view, name="department-get"),
    path("create/", department_create_view, name="department-create"),
    path("update/", department_update_view, name="department-update"),
    path(
        "inactivate/",
        department_inactivate_view,
        name="department-inactivate"),
    path("restore/", department_restore_view, name="department-restore"),
    path("annul/", department_annul_view, name="department-annul"),
    path("export/", department_export_view, name="department-export"),
    path("template/", department_template_view, name="department-template"),
    path("import/", department_import_view, name="department-import"),
    path("log/", department_log_view, name="department-log"),
    path(
        "log/detail/",
        department_log_detail_view,
        name="department-log-detail"),
]
