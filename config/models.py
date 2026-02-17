import uuid

from django.conf import settings
from django.db import models


class TypeStatus(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=50)
    description = models.TextField()

    def __str__(self):
        return self.name

    class Meta:
        db_table = "config_type_status"


class Status(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=50)
    description = models.TextField()
    color_code = models.CharField(
        max_length=7, default="#6C757D", help_text="Hex color code (e.g., #28A745)"
    )
    icon = models.CharField(
        max_length=50, null=True, blank=True, help_text="Icon name (e.g., fas fa-check)"
    )
    type_status = models.ForeignKey(TypeStatus, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    class Meta:
        db_table = "config_status"


class BaseModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    key_user_created = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="%(class)s_created",
    )
    key_user_updated = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="%(class)s_updated",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.ForeignKey(Status, on_delete=models.CASCADE)

    class Meta:
        abstract = True
