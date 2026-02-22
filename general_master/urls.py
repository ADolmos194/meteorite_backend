from django.urls import path, include

urlpatterns = [
    path("", include("general_master.config_master.urls")),
]
