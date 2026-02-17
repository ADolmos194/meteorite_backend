from django.urls import path

from .views import *

urlpatterns = [
    path("country/get/", country_get_view, name="country-get"),
    path("country/create/", country_create_view, name="country-create"),
    path("country/update/", country_update_view, name="country-update"),
    path("country/inactivate/", country_inactivate_view, name="country-inactivate"),
    path("country/restore/", country_restore_view, name="country-restore"),
    path("country/annul/", country_annul_view, name="country-annul"),
    path("country/export/", country_export_view, name="country-export"),
    path("country/template/", country_template_view, name="country-template"),
    path("country/import/", country_import_view, name="country-import"),
]
