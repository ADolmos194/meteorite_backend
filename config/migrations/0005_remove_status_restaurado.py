import uuid

from django.db import migrations


def remove_status_restaurado(apps, schema_editor):
    Status = apps.get_model("config", "Status")
    # UUID for STATUS_RESTAURADO
    restaurado_uuid = uuid.UUID("541e603a-32f4-4ea2-94a4-eb7cbfcc790a")
    Status.objects.filter(id=restaurado_uuid).delete()


def reverse_remove_status_restaurado(apps, schema_editor):
    # If we need to revert, we could re-add it, but usually not necessary
    # for a "cleanup" migration unless explicitly required.
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("config", "0004_seed_statuses"),  # Depends on the seeding migration
    ]

    operations = [
        migrations.RunPython(
            remove_status_restaurado, reverse_remove_status_restaurado
        ),
    ]
