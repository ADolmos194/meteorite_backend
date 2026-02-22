from django.urls import path
from ..views.country import (
    country_get_view,
    country_select_view,
    country_create_view,
    country_update_view,
    country_inactivate_view,
    country_restore_view,
    country_annul_view,
    country_export_view,
    country_template_view,
    country_import_view,
    country_log_view,
    country_log_detail_view,
)

urlpatterns = [
    path("get/", country_get_view, name="country-get"),
    path("select/", country_select_view, name="country-select"),
    path("create/", country_create_view, name="country-create"),
    path("update/", country_update_view, name="country-update"),
    path("inactivate/", country_inactivate_view, name="country-inactivate"),
    path("restore/", country_restore_view, name="country-restore"),
    path("annul/", country_annul_view, name="country-annul"),
    path("export/", country_export_view, name="country-export"),
    path("template/", country_template_view, name="country-template"),
    path("import/", country_import_view, name="country-import"),
    path("log/", country_log_view, name="country-log"),
    path("log/detail/", country_log_detail_view, name="country-log-detail"),
]
