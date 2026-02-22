from django.db.models import Q
from config.utils import STATUS_ACTIVO, STATUS_INACTIVO
from .models import Country, Department


def validate_department_import_row(row_data, seen_codes):
    """
    Valida una fila individual del Excel para Departamento y retorna (es_valido, errores_dict).
    """
    code = str(row_data.get("CÓDIGO", "")).strip().upper()
    name = str(row_data.get("NOMBRE", "")).strip().upper()
    abbr = str(row_data.get("ABREVIACIÓN", "")).strip().upper()
    country_val = str(row_data.get("PAÍS", "")).strip()
    status_name = str(row_data.get("ESTADO", "")).strip().upper()

    # Actualizar row_data con los valores corregidos
    row_data["CÓDIGO"] = code
    row_data["NOMBRE"] = name
    row_data["ABREVIACIÓN"] = abbr

    errors = {}

    if not code:
        errors["CÓDIGO"] = "El código es obligatorio"
    if not name:
        errors["NOMBRE"] = "El nombre es obligatorio"
    if not abbr:
        errors["ABREVIACIÓN"] = "La abreviación es obligatoria"
    if not country_val:
        errors["PAÍS"] = "El país es obligatorio"

    # Buscar el país SOLO por nombre y SOLO si está Activo
    country = None
    if country_val:
        country = Country.objects.filter(
            name__iexact=country_val,
            status_id=STATUS_ACTIVO
        ).first()
        if not country:
            errors["PAÍS"] = f"País activo '{country_val}' no encontrado"
        else:
            # Inject UUID for the handler's auto-merge but keep the name in "PAÍS" for display
            row_data["key_country_id"] = str(country.id)

    if status_name:
        if status_name == "ACTIVO":
            row_data["status_id"] = STATUS_ACTIVO
        elif status_name == "INACTIVO":
            row_data["status_id"] = STATUS_INACTIVO
        else:
            errors["ESTADO"] = "El estado debe ser 'Activo' o 'Inactivo'"
    else:
        row_data["status_id"] = STATUS_ACTIVO

    if errors:
        return False, errors

    # Verificar duplicados en el mismo archivo (combinación código + país)
    row_key = f"{code}_{country.id}"
    if row_key in seen_codes:
        errors["CÓDIGO"] = f"Código '{code}' duplicado para este país en el archivo"
        return False, errors
    seen_codes.add(row_key)

    # Verificar duplicados en la base de datos
    exists = Department.objects.filter(
        Q(code=code) | Q(name=name),
        key_country_id=country.id,
        status_id__in=[STATUS_ACTIVO, STATUS_INACTIVO],
    ).exists()

    if exists:
        if Department.objects.filter(code=code, key_country_id=country.id, status_id__in=[STATUS_ACTIVO, STATUS_INACTIVO]).exists():
            errors["CÓDIGO"] = f"El código '{code}' ya existe en este país"
        if Department.objects.filter(name=name, key_country_id=country.id, status_id__in=[STATUS_ACTIVO, STATUS_INACTIVO]).exists():
            errors["NOMBRE"] = f"El nombre '{name}' ya existe en este país"
        
        if not errors:
            errors["CÓDIGO"] = "Registro duplicado en base de datos para este país"
        return False, errors

    return True, {}

# Mensajes de error para la importación
MSG_COLUMN_MISSING = (
    "El archivo Excel no tiene las columnas requeridas: "
    "CÓDIGO, NOMBRE, ABREVIACIÓN, ISO2, ISO3, NÚMERO DE PREFIJO"
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
    code = str(row_data.get("CÓDIGO", "")).strip().upper()
    name = str(row_data.get("NOMBRE", "")).strip().upper()
    abbr = str(row_data.get("ABREVIACIÓN", "")).strip().upper()
    iso2 = str(row_data.get("ISO2", "")).strip().upper()
    iso3 = str(row_data.get("ISO3", "")).strip().upper()
    phone = str(row_data.get("NÚMERO DE PREFIJO", "")).strip().upper()
    status_name = str(row_data.get("ESTADO", "")).strip().upper()

    # Actualizar row_data con los valores en mayúsculas para la persistencia
    row_data["CÓDIGO"] = code
    row_data["NOMBRE"] = name
    row_data["ABREVIACIÓN"] = abbr
    row_data["ISO2"] = iso2
    row_data["ISO3"] = iso3
    row_data["NÚMERO DE PREFIJO"] = phone

    errors = {}

    if not code:
        errors["CÓDIGO"] = "El código es obligatorio"
    if not name:
        errors["NOMBRE"] = "El nombre es obligatorio"
    if not abbr:
        errors["ABREVIACIÓN"] = "La abreviación es obligatoria"

    if iso2 and len(iso2) != 2:
        errors["ISO2"] = "El código ISO2 debe tener exactamente 2 caracteres"
    if iso3 and len(iso3) != 3:
        errors["ISO3"] = "El código ISO3 debe tener exactamente 3 caracteres"

    if status_name:
        if status_name == "ACTIVO":
            row_data["status_id"] = STATUS_ACTIVO
        elif status_name == "INACTIVO":
            row_data["status_id"] = STATUS_INACTIVO
        else:
            errors["ESTADO"] = "El estado debe ser 'Activo' o 'Inactivo'"
    else:
        # Default if column is empty but present
        row_data["status_id"] = STATUS_ACTIVO

    if errors:
        return False, errors

    # Verificar duplicados en el mismo archivo
    if code in seen_codes:
        errors["CÓDIGO"] = MSG_DUPLICATE_IN_FILE.format(code=code)
        return False, errors

    # Verificar duplicados en la base de datos (Activos/Inactivos)
    exists = Country.objects.filter(
        Q(code=code) | Q(name=name) | Q(abbreviation=abbr),
        status_id__in=[STATUS_ACTIVO, STATUS_INACTIVO],
    ).exists()

    if not exists and iso2:
        exists = Country.objects.filter(
            iso_alpha_2=iso2, status_id__in=[STATUS_ACTIVO, STATUS_INACTIVO]
        ).exists()
    if not exists and iso3:
        exists = Country.objects.filter(
            iso_alpha_3=iso3, status_id__in=[STATUS_ACTIVO, STATUS_INACTIVO]
        ).exists()

    if exists:
        # Intentar ser más específico si es posible
        if Country.objects.filter(
            code=code, status_id__in=[STATUS_ACTIVO, STATUS_INACTIVO]
        ).exists():
            errors["CÓDIGO"] = f"El código '{code}' ya existe"
        if Country.objects.filter(
            name=name, status_id__in=[STATUS_ACTIVO, STATUS_INACTIVO]
        ).exists():
            errors["NOMBRE"] = f"El nombre '{name}' ya existe"
        if iso2 and Country.objects.filter(
            iso_alpha_2=iso2, status_id__in=[STATUS_ACTIVO, STATUS_INACTIVO]
        ).exists():
            errors["ISO2"] = f"El ISO2 '{iso2}' ya existe"
        if iso3 and Country.objects.filter(
            iso_alpha_3=iso3, status_id__in=[STATUS_ACTIVO, STATUS_INACTIVO]
        ).exists():
            errors["ISO3"] = f"El ISO3 '{iso3}' ya existe"

        if not errors:  # Caso borde (duplicado por combinación or)
            errors["CÓDIGO"] = "Registro duplicado en base de datos"

        return False, errors

    return True, {}
