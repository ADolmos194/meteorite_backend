from django.db import migrations

def seed_audit_events(apps, schema_editor):
    Event = apps.get_model('access', 'Event')
    # Use same IDs as in audit/utils.py for consistency
    events_to_create = [
        {
            "id": "a92b49fc-3690-4200-80b7-5a883279599e",
            "name": "ACTUALIZACIÓN",
            "description": "Modificación de un registro existente"
        },
        {
            "id": "c57fd4e8-7108-4e96-9f5a-0ff5e5f69afb",
            "name": "INACTIVACIÓN",
            "description": "El registro pasa a estado Inactivo"
        },
        {
            "id": "b443609e-a554-4e38-bc3e-0e1a82792f35",
            "name": "RESTAURACIÓN",
            "description": "El registro pasa de Inactivo/Anulado a Activo"
        },
        {
            "id": "fe29663e-12f2-40b9-90af-2c1f8ff8630a",
            "name": "ANULACIÓN",
            "description": "El registro pasa a estado Anulado"
        }
    ]
    
    # Needs a valid user for key_user_created_id and key_user_updated_id
    # We'll use the first user found or a hardcoded one if known
    User = apps.get_model('meteorite_auth', 'User')
    user = User.objects.first()
    user_id = user.id if user else None
    
    # Needs a valid status to match BaseModel requirements
    Status = apps.get_model('config', 'Status')
    active_status = Status.objects.filter(id="2bd04756-cf71-438d-b8be-7d6dd58e5e34").first()

    for event_data in events_to_create:
        Event.objects.get_or_create(
            id=event_data["id"],
            defaults={
                "name": event_data["name"],
                "description": event_data["description"],
                "key_user_created_id": user_id,
                "key_user_updated_id": user_id,
                "status": active_status
            }
        )

def remove_audit_events(apps, schema_editor):
    Event = apps.get_model('access', 'Event')
    ids_to_remove = [
        "a92b49fc-3690-4200-80b7-5a883279599e",
        "c57fd4e8-7108-4e96-9f5a-0ff5e5f69afb",
        "b443609e-a554-4e38-bc3e-0e1a82792f35",
        "fe29663e-12f2-40b9-90af-2c1f8ff8630a"
    ]
    Event.objects.filter(id__in=ids_to_remove).delete()

class Migration(migrations.Migration):
    dependencies = [
        ("access", "0003_rolemenu"),
        ("config", "0001_initial"), # Ensure Status model exists
    ]

    operations = [
        migrations.RunPython(seed_audit_events, reverse_code=remove_audit_events),
    ]
