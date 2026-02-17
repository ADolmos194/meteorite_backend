from django.urls import path

from . import views

urlpatterns = [
    path("status/all/", views.get_all_statuses, name="get_all_statuses"),
]
