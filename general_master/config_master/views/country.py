import copy
from django.db import transaction
from rest_framework import status
from rest_framework.decorators import api_view
from drf_spectacular.utils import extend_schema, OpenApiTypes

from config.excel_handler import ExcelMasterHandler
from config.utils import (
    STATUS_ACTIVO,
    STATUS_ANULADO,
    STATUS_INACTIVO,
    MiddlewareAutentication,
    errorcall,
    succescall,
)

from audit.utils import (
    EVENT_ANNUL,
    EVENT_CREATE,
    EVENT_INACTIVATE,
    EVENT_RESTORE,
    EVENT_UPDATE,
    EVENT_IMPORT,
    EVENT_MASS_ACTIVATE,
    EVENT_MASS_INACTIVATE,
    EVENT_MASS_ANNUL,
    save_audit_log,
)
from ..import_validators import validate_country_import_row
from ..models import Country
from ..serializers import CountrySerializer
from audit.models import AuditLog, AuditLogDetail
from audit.serializers import AuditLogSerializer, AuditLogDetailSerializer


@extend_schema(request=None, responses={200: CountrySerializer(many=True)})
@MiddlewareAutentication("general_master_country_get")
@api_view(["POST"])
def country_get_view(request):
    status_filter = request.data.get("status", None)
    page = int(request.data.get("page", 1))
    page_size = min(int(request.data.get("page_size", 10)), 200)

    qs = Country.objects.exclude(status_id=STATUS_ANULADO)
    if status_filter == "activo":
        qs = Country.objects.filter(status_id=STATUS_ACTIVO)
    elif status_filter == "inactivo":
        qs = Country.objects.filter(status_id=STATUS_INACTIVO)

    qs = qs.order_by("-created_at")
    total = qs.count()
    start = (page - 1) * page_size
    end = start + page_size
    serializer = CountrySerializer(qs[start:end], many=True)
    return succescall(
        {
            "results": serializer.data,
            "total": total,
            "page": page,
            "page_size": page_size,
            "pages": (total + page_size - 1) // page_size,
        },
        "Lista de países obtenida correctamente",
    )


@extend_schema(responses={200: CountrySerializer(many=True)})
@MiddlewareAutentication("general_master_country_get")
@api_view(["GET"])
def country_select_view(request):
    """
    Endpoint optimizado para selectores/dropdowns.
    Solo retorna países ACTIVOS con los campos mínimos necesarios: id y name.
    """
    countries = list(
        Country.objects.filter(
            status_id=STATUS_ACTIVO).order_by("name").values(
            "id", "name"))
    return succescall(
        {"results": countries, "total": len(countries)},
        "Lista de países activos para selector obtenida correctamente",
    )


@extend_schema(request=CountrySerializer, responses={201: CountrySerializer})
@api_view(["POST"])
@MiddlewareAutentication("general_master_country_create")
def country_create_view(request):
    from django.db.models import Q
    code = str(request.data.get("code", "")).strip().upper()
    name = str(request.data.get("name", "")).strip().upper()
    abbreviation = str(request.data.get("abbreviation", "")).strip().upper()

    exists = Country.objects.filter(
        Q(code=code) | Q(name=name) | Q(abbreviation=abbreviation),
        status_id__in=[STATUS_ACTIVO, STATUS_INACTIVO],
    ).exists()

    if exists:
        return errorcall(
            "Ya existe un país con ese código, nombre o abreviación "
            "activo/inactivo",
            status.HTTP_400_BAD_REQUEST,
        )

    mutable_data = request.data.copy()
    mutable_data["code"] = code
    mutable_data["name"] = name
    mutable_data["abbreviation"] = abbreviation

    serializer = CountrySerializer(data=mutable_data)
    if serializer.is_valid():
        instance = serializer.save(
            key_user_created_id=request.user.id,
            key_user_updated_id=request.user.id,
            status_id=STATUS_ACTIVO,
        )
        save_audit_log(instance, request.user.id, EVENT_CREATE)
        return succescall(serializer.data, "País creado correctamente")
    return errorcall(serializer.errors, status.HTTP_400_BAD_REQUEST)


@extend_schema(request=CountrySerializer, responses={200: CountrySerializer})
@api_view(["PATCH"])
@MiddlewareAutentication("general_master_country_update")
def country_update_view(request):
    from django.db.models import Q
    pk = request.data.get("id")
    country = Country.objects.filter(pk=pk).first()
    if not country:
        return errorcall("País no encontrado", status.HTTP_404_NOT_FOUND)

    code = str(request.data.get("code", country.code)).strip().upper()
    name = str(request.data.get("name", country.name)).strip().upper()
    abbreviation = str(
        request.data.get("abbreviation", country.abbreviation)
    ).strip().upper()

    exists = (
        Country.objects.filter(
            Q(code=code) | Q(name=name) | Q(abbreviation=abbreviation),
            status_id__in=[STATUS_ACTIVO, STATUS_INACTIVO],
        )
        .exclude(pk=pk)
        .exists()
    )

    if exists:
        return errorcall(
            "Ya existe otro país con ese código, nombre o abreviación "
            "activo/inactivo",
            status.HTTP_400_BAD_REQUEST,
        )

    old_instance = copy.copy(country)

    mutable_data = request.data.copy()
    mutable_data["code"] = code
    mutable_data["name"] = name
    mutable_data["abbreviation"] = abbreviation

    serializer = CountrySerializer(country, data=mutable_data, partial=True)
    if serializer.is_valid():
        instance = serializer.save(key_user_updated_id=request.user.id)
        save_audit_log(instance, request.user.id, EVENT_UPDATE, old_instance)
        return succescall(serializer.data, "País actualizado correctamente")
    return errorcall(serializer.errors, status.HTTP_400_BAD_REQUEST)


@extend_schema(request=None, responses={200: OpenApiTypes.STR})
@api_view(["PATCH"])
@MiddlewareAutentication("general_master_country_inactivate")
def country_inactivate_view(request):
    pks = request.data.get("ids", [])
    pk = request.data.get("id")
    if pk:
        pks.append(pk)

    if not pks:
        return errorcall("IDs no proporcionados", status.HTTP_400_BAD_REQUEST)

    countries = Country.objects.filter(pk__in=pks)
    if not countries.exists():
        return errorcall("Países no encontrados", status.HTTP_404_NOT_FOUND)

    is_mass = bool(request.data.get("ids", []))
    event_type = EVENT_MASS_INACTIVATE if is_mass else EVENT_INACTIVATE

    count = 0
    with transaction.atomic():
        for country in countries:
            country.status_id = STATUS_INACTIVO
            country.key_user_updated_id = request.user.id
            country.save()
            save_audit_log(country, request.user.id, event_type)
            count += 1

    return succescall(None, f"{count} países inactivados correctamente")


@extend_schema(request=None, responses={200: OpenApiTypes.STR})
@api_view(["PATCH"])
@MiddlewareAutentication("general_master_country_restore")
def country_restore_view(request):
    pks = request.data.get("ids", [])
    pk = request.data.get("id")
    if pk:
        pks.append(pk)

    if not pks:
        return errorcall("IDs no proporcionados", status.HTTP_400_BAD_REQUEST)

    countries = Country.objects.filter(pk__in=pks)
    if not countries.exists():
        return errorcall("Países no encontrados", status.HTTP_404_NOT_FOUND)

    is_mass = bool(request.data.get("ids", []))
    event_type = EVENT_MASS_ACTIVATE if is_mass else EVENT_RESTORE

    count = 0
    with transaction.atomic():
        for country in countries:
            country.status_id = STATUS_ACTIVO
            country.key_user_updated_id = request.user.id
            country.save()
            save_audit_log(country, request.user.id, event_type)
            count += 1

    return succescall(None, f"{count} países restaurados correctamente")


@extend_schema(request=None, responses={200: OpenApiTypes.STR})
@api_view(["PATCH"])
@MiddlewareAutentication("general_master_country_annul")
def country_annul_view(request):
    pks = request.data.get("ids", [])
    pk = request.data.get("id")
    if pk:
        pks.append(pk)

    if not pks:
        return errorcall("IDs no proporcionados", status.HTTP_400_BAD_REQUEST)

    countries = Country.objects.filter(pk__in=pks)
    if not countries.exists():
        return errorcall("Países no encontrados", status.HTTP_404_NOT_FOUND)

    is_mass = bool(request.data.get("ids", []))
    event_type = EVENT_MASS_ANNUL if is_mass else EVENT_ANNUL

    count = 0
    with transaction.atomic():
        for country in countries:
            country.status_id = STATUS_ANULADO
            country.key_user_updated_id = request.user.id
            country.save()
            save_audit_log(country, request.user.id, event_type)
            count += 1

    return succescall(None, f"{count} países anulados correctamente")


@extend_schema(request=None, responses={200: AuditLogSerializer(many=True)})
@MiddlewareAutentication("general_master_country_log")
@api_view(["POST"])
def country_log_view(request):
    pk = request.data.get("id")
    if not pk:
        return errorcall("ID no proporcionado", status.HTTP_400_BAD_REQUEST)

    country = Country.objects.filter(pk=pk).first()
    if not country:
        return errorcall("País no encontrado", status.HTTP_404_NOT_FOUND)

    logs = AuditLog.objects.filter(
        record_id=pk,
        name_table=Country._meta.db_table
    ).order_by("-created_at")
    serializer = AuditLogSerializer(logs, many=True)
    return succescall(serializer.data, "Logs del país obtenidos correctamente")


@extend_schema(
    request=None,
    responses={200: AuditLogDetailSerializer(many=True)})
@MiddlewareAutentication("general_master_country_log_detail")
@api_view(["POST"])
def country_log_detail_view(request):
    pk = request.data.get("id")
    if not pk:
        return errorcall("ID no proporcionado", status.HTTP_400_BAD_REQUEST)

    log = AuditLog.objects.filter(pk=pk).first()
    if not log:
        return errorcall("Log no encontrado", status.HTTP_404_NOT_FOUND)

    details = AuditLogDetail.objects.filter(
        key_audit_log=log,
        key_audit_log__name_table=Country._meta.db_table
    )
    serializer = AuditLogDetailSerializer(details, many=True)
    return succescall(
        serializer.data,
        "Detalles del log obtenidos correctamente")


@extend_schema(request=None, responses={200: OpenApiTypes.STR})
@api_view(["GET"])
@MiddlewareAutentication("general_master_country_export")
def country_export_view(request):
    countries = Country.objects.exclude(
        status_id=STATUS_ANULADO
    ).order_by("name")
    headers = [
        "CÓDIGO",
        "NOMBRE",
        "ABREVIACIÓN",
        "ISO2",
        "ISO3",
        "NÚMERO DE PREFIJO",
        "ESTADO"]
    handler = ExcelMasterHandler(Country, headers, "paises", request.user.id)

    field_mapping = {
        "code": "CÓDIGO",
        "name": "NOMBRE",
        "abbreviation": "ABREVIACIÓN",
        "iso_alpha_2": "ISO2",
        "iso_alpha_3": "ISO3",
        "phone_prefix": "NÚMERO DE PREFIJO",
        "status_name": "ESTADO",
    }
    return handler.export_data(countries, CountrySerializer, field_mapping)


@extend_schema(request=None, responses={200: OpenApiTypes.STR})
@api_view(["GET"])
@MiddlewareAutentication("general_master_country_template")
def country_template_view(request):
    headers = [
        "CÓDIGO",
        "NOMBRE",
        "ABREVIACIÓN",
        "ISO2",
        "ISO3",
        "NÚMERO DE PREFIJO",
        "ESTADO"]
    handler = ExcelMasterHandler(Country, headers, "paises", request.user.id)
    return handler.generate_template()


@extend_schema(request=None, responses={200: OpenApiTypes.STR})
@api_view(["POST"])
@MiddlewareAutentication("general_master_country_import")
@transaction.atomic
def country_import_view(request):
    headers = [
        "CÓDIGO",
        "NOMBRE",
        "ABREVIACIÓN",
        "ISO2",
        "ISO3",
        "NÚMERO DE PREFIJO",
        "ESTADO"]
    handler = ExcelMasterHandler(Country, headers, "paises", request.user.id)

    field_mapping = {
        "CÓDIGO": "code",
        "NOMBRE": "name",
        "ABREVIACIÓN": "abbreviation",
        "ISO2": "iso_alpha_2",
        "ISO3": "iso_alpha_3",
        "NÚMERO DE PREFIJO": "phone_prefix",
        "status_id": "status_id",
    }

    def _audit_import(instance):
        save_audit_log(instance, request.user.id, EVENT_IMPORT)

    return handler.import_data(
        request,
        validate_country_import_row,
        field_mapping,
        audit_save_fn=_audit_import)
