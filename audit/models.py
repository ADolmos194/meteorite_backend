import uuid

from django.db import models


class AuditLog(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    key_event = models.UUIDField(db_index=True)
    name_module = models.CharField(max_length=50, db_index=True)
    name_table = models.CharField(max_length=50, db_index=True)

    record_id = models.UUIDField(db_index=True)

    key_user = models.UUIDField(db_index=True)

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    def __str__(self):
        return f"{self.name_table} - {self.key_event}"

    class Meta:
        db_table = "audit_log"


class AuditLogDetail(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    key_audit_log = models.ForeignKey(
        AuditLog, on_delete=models.CASCADE, related_name="details"
    )

    column_name = models.CharField(max_length=50, db_index=True)
    old_value = models.TextField(null=True, blank=True)
    new_value = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.column_name

    class Meta:
        db_table = "audit_log_detail"
