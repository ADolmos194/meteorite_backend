from django.db import models
from .models import AuditLog, AuditLogDetail

# ---------------------------------------------------------
# CONSTANTES DE EVENTOS DE AUDITORÍA (UUIDs Únicos)
# ---------------------------------------------------------
EVENT_CREATE = "fd9c7022-581c-4f60-b22b-653138544474"
EVENT_UPDATE = "a92b49fc-3690-4200-80b7-5a883279599e"
EVENT_INACTIVATE = "c57fd4e8-7108-4e96-9f5a-0ff5e5f69afb"
EVENT_RESTORE = "b443609e-a554-4e38-bc3e-0e1a82792f35"
EVENT_ANNUL = "fe29663e-12f2-40b9-90af-2c1f8ff8630a"
EVENT_IMPORT = "8faad2e0-7a71-4225-aa1b-23ba2d04062d"
EVENT_MASS_ACTIVATE = "a801a75d-d648-4006-ac4b-af5777f83691"
EVENT_MASS_INACTIVATE = "4dfc1fff-1845-4a38-8c14-1233448f0aed"
EVENT_MASS_ANNUL = "dc1e860e-b22f-4a62-9eac-20b0f00e3489"

EVENT_NAMES = {
    EVENT_CREATE: "CREACIÓN",
    EVENT_UPDATE: "ACTUALIZACIÓN",
    EVENT_INACTIVATE: "INACTIVACIÓN",
    EVENT_RESTORE: "RESTAURACIÓN",
    EVENT_ANNUL: "ANULACIÓN",
    EVENT_IMPORT: "IMPORTACIÓN",
    EVENT_MASS_ACTIVATE: "ACTIVACIÓN MASIVA",
    EVENT_MASS_INACTIVATE: "INACTIVACIÓN MASIVA",
    EVENT_MASS_ANNUL: "ANULACIÓN MASIVA",
}


def save_audit_log(instance, user_id, event_type, old_instance=None):
    try:
        # 1. Crear el encabezado de auditoría
        audit_log = AuditLog.objects.create(
            key_event=event_type,
            name_module=instance._meta.app_label,
            name_table=instance._meta.db_table,
            record_id=instance.id,
            key_user=user_id
        )

        # 2. Si es una creación, opcionalmente podrías loguear todos los
        # campos iniciales o simplemente dejar el encabezado. Por simplicidad,
        # solo logueamos cambios en UPDATES.
        if event_type == EVENT_UPDATE and old_instance:
            compare_and_save_details(audit_log, instance, old_instance)

        return audit_log
    except Exception as e:
        # Loguear el error si es necesario, pero no detener el flujo principal
        print(f"Error saving audit log: {e}")
        return None


def compare_and_save_details(audit_log, instance, old_instance):
    """
    Compara los campos de dos instancias y guarda los detalles de auditoría.
    """
    # Lista de campos a ignorar (metadatos internos)
    exclude_fields = [
        'created_at',
        'updated_at',
        'key_user_created',
        'key_user_updated']

    details = []

    for field in instance._meta.fields:
        field_name = field.name
        if field_name in exclude_fields:
            continue

        old_val = getattr(old_instance, field_name)
        new_val = getattr(instance, field_name)

        # Comparar valores (manejar objetos ForeignKey obteniendo su ID o
        # __str__)
        if old_val != new_val:
            # Convertir a string para almacenamiento en TextField
            str_old = str(
                old_val.id) if isinstance(
                old_val,
                models.Model) else str(old_val)
            str_new = str(
                new_val.id) if isinstance(
                new_val,
                models.Model) else str(new_val)

            # Si el valor anterior era None, guardar como string vacío o "None"
            if old_val is None:
                str_old = ""
            if new_val is None:
                str_new = ""

            details.append(AuditLogDetail(
                key_audit_log=audit_log,
                column_name=field_name,
                old_value=str_old,
                new_value=str_new
            ))

    if details:
        AuditLogDetail.objects.bulk_create(details)
