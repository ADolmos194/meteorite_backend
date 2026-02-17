from django.db.models import Q
from config.utils import STATUS_ACTIVO, STATUS_INACTIVO
from .models import Country

# Mensajes de error para la importación
MSG_COLUMN_MISSING = (
    "El archivo Excel no tiene las columnas requeridas: "
    "Código, Nombre, Abreviación"
)
MSG_EMPTY_FILE = "El archivo Excel está vacío"
MSG_DUPLICATE_IN_FILE = (
    "Se encontró un código duplicado dentro del mismo archivo Excel: {code}"
)
MSG_DUPLICATE_IN_DB = (
    "El país con código '{code}' o nombre '{name}' "
    "ya existe en estado Activo o Inactivo"
)
MSG_INVALID_FORMAT = "El formato de fila es inválido en la fila {row}"


def validate_country_import_row(row_data, seen_codes):
    """
    Valida una fila individual del Excel y retorna (es_valido, errores_dict).
    """
    code = str(row_data.get("Código", "")).strip()
    name = str(row_data.get("Nombre", "")).strip()
    abbr = str(row_data.get("Abreviación", "")).strip()
    status_name = str(row_data.get("Estado", "")).strip().upper()

    errors = {}

    if not code:
        errors["Código"] = "El código es obligatorio"
    if not name:
        errors["Nombre"] = "El nombre es obligatorio"
    if not abbr:
        errors["Abreviación"] = "La abreviación es obligatoria"

    if status_name:
        if status_name == "ACTIVO":
            row_data["status_id"] = STATUS_ACTIVO
        elif status_name == "INACTIVO":
            row_data["status_id"] = STATUS_INACTIVO
        else:
            errors["Estado"] = "El estado debe ser 'Activo' o 'Inactivo'"
    else:
        # Default if column is empty but present
        row_data["status_id"] = STATUS_ACTIVO

    if errors:
        return False, errors

    # Verificar duplicados en el mismo archivo
    if code in seen_codes:
        errors["Código"] = MSG_DUPLICATE_IN_FILE.format(code=code)
        return False, errors

    # Verificar duplicados en la base de datos (Activos/Inactivos)
    exists = Country.objects.filter(
        Q(code=code) | Q(name=name),
        status_id__in=[STATUS_ACTIVO, STATUS_INACTIVO],
    ).exists()

    if exists:
        # Intentar ser más específico si es posible
        if Country.objects.filter(
            code=code, status_id__in=[STATUS_ACTIVO, STATUS_INACTIVO]
        ).exists():
            errors["Código"] = f"El código '{code}' ya existe"
        if Country.objects.filter(
            name=name, status_id__in=[STATUS_ACTIVO, STATUS_INACTIVO]
        ).exists():
            errors["Nombre"] = f"El nombre '{name}' ya existe"

        if not errors:  # Caso borde (duplicado por combinación or)
            errors["Código"] = "Registro duplicado en base de datos"

        return False, errors

    return True, {}
