from django.apps import AppConfig


class ConfigMasterConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "general_master.config_master"
    label = "general_master_config_master"
