import uuid

from django.db import migrations


def seed_statuses(apps, schema_editor):
    TypeStatus = apps.get_model("config", "TypeStatus")
    Status = apps.get_model("config", "Status")

    # Ensure TypeStatus exists
    type_status, _ = TypeStatus.objects.get_or_create(
        id=uuid.UUID("853663dd-9c99-43f6-92af-e81fe83681f6"),
        defaults={
            "name": "MAESTRA",
            "description": "Estados generales para tablas maestras",
        },
    )

    statuses = [
        (
            "ab8a2bef-e236-4d73-99b1-f8c988be2e99",
            "BORRADOR",
            "Para registros que aún se están editando y no deben ser visibles en el sistema principal.",
            "#6C757D",
            "i-lucide-file-text",
        ),
        (
            "09618606-d931-428a-aee4-e45032c00310",
            "EN REVISIÓN",
            "El registro ha sido enviado para validación.",
            "#0D6EFD",
            "i-lucide-eye",
        ),
        (
            "6d025ac4-3d4f-4889-b9d2-64afc723c299",
            "APROBADO",
            "Validado y listo para su uso",
            "#198754",
            "i-lucide-check-circle",
        ),
        (
            "c370c327-f93d-4cc6-b566-8945da77ee0d",
            "RECHAZADO",
            "No pasó la validación",
            "#DC3545",
            "i-lucide-x-circle",
        ),
        (
            "45eca1ed-2f98-4b92-b677-492d190cae86",
            "BLOQUEADO",
            "El registro existe pero su uso está restringido temporalmente por razones de seguridad o sistema",
            "#FD7E14",
            "i-lucide-lock",
        ),
        (
            "91adf4bd-e05d-4230-9fd9-6510d6889516",
            "SUSPENDIDO",
            "Similar a inactivo, pero suele implicar una pausa temporal.",
            "#FFC107",
            "i-lucide-pause-circle",
        ),
        (
            "29f770db-5d6b-49c9-8b58-87ede5b395fd",
            "EXPIRADO",
            "Útil si manejas registros con fechas de vigencia (como tokens, contratos o membresías).",
            "#495057",
            "i-lucide-clock",
        ),
        (
            "a12400ea-0643-4ea1-ab7d-b9b54d55b0e8",
            "ERROR",
            "Cuando un proceso automático falló al intentar crear o modificar el registro.",
            "#B02A37",
            "i-lucide-alert-triangle",
        ),
        (
            "b4d35209-2fa2-422c-bf81-d647599310a5",
            "ENVIADO",
            "El registro fue mandado a un servicio externo",
            "#0DCAF0",
            "i-lucide-send",
        ),
        (
            "8e5124d7-b0f1-4db0-820e-625f66b9b3b2",
            "RECIBIDO",
            "Confirmación de recepción de un tercero.",
            "#6610F2",
            "i-lucide-inbox",
        ),
        (
            "c2807e6c-1730-46cc-8ede-3cb5bdf623e8",
            "FALLIDO",
            "Error en la comunicación externa.",
            "#DC3545",
            "i-lucide-cloud-off",
        ),
        (
            "995a6208-2818-423c-badb-727237c967df",
            "SINCRONIZADO",
            "El registro está al día con otros sistemas",
            "#20C997",
            "i-lucide-refresh-cw",
        ),
        (
            "e217fae9-6cf8-4a32-b2d2-d5de1adf6c00",
            "ARCHIVADO",
            "Registros antiguos que no se usan pero que deben conservarse por historial",
            "#795548",
            "i-lucide-archive",
        ),
        (
            "2bd04756-cf71-438d-b8be-7d6dd58e5e34",
            "ACTIVO",
            "Registro vigente, operativo y visible en las consultas principales del sistema.",
            "#28A745",
            "i-lucide-play",
        ),
        (
            "742ab54f-c5ab-4a41-93e3-373e1d9c4105",
            "INACTIVO",
            "Registro deshabilitado manualmente; conserva integridad pero no permite operaciones.",
            "#6C757D",
            "i-lucide-stop-circle",
        ),
        (
            "bd7a3ed1-efdb-429b-9cb2-9999b7a12bab",
            "ANULADO",
            "Registro invalidado por error administrativo o cancelación de un proceso.",
            "#FD7E14",
            "i-lucide-slash",
        ),
        (
            "541e603a-32f4-4ea2-94a4-eb7cbfcc790a",
            "RESTAURADO",
            "Registro recuperado exitosamente tras haber sido eliminado o anulado previamente.",
            "#0D6EFD",
            "i-lucide-refresh-ccw",
        ),
        (
            "87ed0a4c-df78-4c53-8fd8-0463d634ec98",
            "ELIMINADO",
            "Registro marcado como borrado lógico; no visible para el usuario final pero conservado por auditoría.",
            "#DC3545",
            "i-lucide-trash-2",
        ),
        (
            "ff2b0252-5a55-4789-90e6-a18ac3f6e569",
            "PENDIENTE",
            "Registro creado que se encuentra a la espera de ser procesado o atendido.",
            "#FFC107",
            "i-lucide-circle-dot",
        ),
        (
            "48d43356-2fd9-494f-989d-113bbfbc6f90",
            "PROCESADO",
            "Registro que ha pasado satisfactoriamente las etapas intermedias de su flujo.",
            "#6F42C1",
            "i-lucide-settings",
        ),
        (
            "139b8dd1-f244-4295-9996-692a66a9c455",
            "COMPLETADO",
            "Registro que ha finalizado todas las etapas de su ciclo de vida con éxito.",
            "#28A745",
            "i-lucide-check-check",
        ),
    ]

    for s_id, name, desc, color, icon in statuses:
        Status.objects.update_or_create(
            id=uuid.UUID(s_id),
            defaults={
                "name": name,
                "description": desc,
                "color_code": color,
                "icon": icon,
                "type_status": type_status,
            },
        )


def remove_statuses(apps, schema_editor):
    Status = apps.get_model("config", "Status")
    # Optional: logic to remove or leave them
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("config", "0003_status_icon"),
    ]

    operations = [
        migrations.RunPython(seed_statuses, remove_statuses),
    ]
