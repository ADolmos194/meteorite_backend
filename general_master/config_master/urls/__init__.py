from django.urls import path, include

urlpatterns = [
    path(
        "country/",
        include("general_master.config_master.urls.country")),
    path(
        "department/",
        include("general_master.config_master.urls.department")),
]
