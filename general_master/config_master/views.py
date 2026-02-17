from django.db import transaction
from django.db.models import Q
from rest_framework import status
from rest_framework.decorators import api_view

from config.excel_handler import ExcelMasterHandler
from config.utils import (
    STATUS_ACTIVO,
    STATUS_ANULADO,
    STATUS_INACTIVO,
    MiddlewareAutentication,
    errorcall,
    succescall,
)

from .import_validators import validate_country_import_row
from .models import Country
from .serializers import CountrySerializer


@MiddlewareAutentication("general_master_country_get")
@api_view(["GET"])
def country_get_view(request):
    countries = Country.objects.exclude(status_id=STATUS_ANULADO).order_by("-created_at")
    total = countries.count()

    serializer = CountrySerializer(countries, many=True)
    return succescall(
        {"results": serializer.data, "total": total},
        "Lista de países obtenida correctamente",
    )


@api_view(["POST"])
@MiddlewareAutentication("general_master_country_create")
def country_create_view(request):
    code = request.data.get("code")
    name = request.data.get("name")

    exists = Country.objects.filter(
        Q(code=code) | Q(name=name),
        status_id__in=[STATUS_ACTIVO, STATUS_INACTIVO],
    ).exists()

    if exists:
        return errorcall(
            "Ya existe un país con ese código o nombre activo/inactivo",
            status.HTTP_400_BAD_REQUEST,
        )

    serializer = CountrySerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(
            key_user_created_id=request.user.id,
            key_user_updated_id=request.user.id,
            status_id=STATUS_ACTIVO,
        )
        return succescall(serializer.data, "País creado correctamente")
    return errorcall(serializer.errors, status.HTTP_400_BAD_REQUEST)


@api_view(["PATCH"])
@MiddlewareAutentication("general_master_country_update")
def country_update_view(request):
    pk = request.data.get("id")
    country = Country.objects.filter(pk=pk).first()
    if not country:
        return errorcall("País no encontrado", status.HTTP_404_NOT_FOUND)

    code = request.data.get("code", country.code)
    name = request.data.get("name", country.name)

    exists = (
        Country.objects.filter(
            Q(code=code) | Q(name=name),
            status_id__in=[STATUS_ACTIVO, STATUS_INACTIVO],
        )
        .exclude(pk=pk)
        .exists()
    )

    if exists:
        return errorcall(
            "Ya existe otro país con ese código o nombre activo/inactivo",
            status.HTTP_400_BAD_REQUEST,
        )

    serializer = CountrySerializer(country, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save(key_user_updated_id=request.user.id)
        return succescall(serializer.data, "País actualizado correctamente")
    return errorcall(serializer.errors, status.HTTP_400_BAD_REQUEST)


@api_view(["PATCH"])
@MiddlewareAutentication("general_master_country_inactivate")
def country_inactivate_view(request):
    pk = request.data.get("id")

    country = Country.objects.filter(pk=pk).first()
    if not country:
        return errorcall("País no encontrado", status.HTTP_404_NOT_FOUND)

    country.status_id = STATUS_INACTIVO
    country.key_user_updated_id = request.user.id
    country.save()
    return succescall(None, "País inactivado correctamente")


@api_view(["PATCH"])
@MiddlewareAutentication("general_master_country_restore")
def country_restore_view(request):
    pk = request.data.get("id")

    country = Country.objects.filter(pk=pk).first()
    if not country:
        return errorcall("País no encontrado", status.HTTP_404_NOT_FOUND)

    country.status_id = STATUS_ACTIVO
    country.key_user_updated_id = request.user.id
    country.save()
    return succescall(None, "País restaurado correctamente")


@api_view(["PATCH"])
@MiddlewareAutentication("general_master_country_annul")
def country_annul_view(request):
    pk = request.data.get("id")
    if not pk:
        return errorcall("ID no proporcionado", status.HTTP_400_BAD_REQUEST)

    country = Country.objects.filter(pk=pk).first()
    if not country:
        return errorcall("País no encontrado", status.HTTP_404_NOT_FOUND)

    country.status_id = STATUS_ANULADO
    country.key_user_updated_id = request.user.id
    country.save()
    return succescall(None, "País anulado correctamente")


@api_view(["GET"])
@MiddlewareAutentication("general_master_country_export")
def country_export_view(request):
    """
    Exporta todos los países (no anulados) a un archivo Excel.
    """
    countries = Country.objects.exclude(
        status_id=STATUS_ANULADO
    ).order_by("name")
    headers = ["Código", "Nombre", "Abreviación", "Estado"]
    handler = ExcelMasterHandler(Country, headers, "paises", request.user.id)

    # El export necesita un mapeo de { 'CampoSerializer': 'TítuloExcel' }
    field_mapping = {
        "code": "Código",
        "name": "Nombre",
        "abbreviation": "Abreviación",
        "status_name": "Estado",
    }
    return handler.export_data(countries, CountrySerializer, field_mapping)


@api_view(["GET"])
@MiddlewareAutentication("general_master_country_template")
def country_template_view(request):
    """
    Descarga la plantilla vacía para la importación.
    """
    headers = ["Código", "Nombre", "Abreviación", "Estado"]
    handler = ExcelMasterHandler(Country, headers, "paises", request.user.id)
    return handler.generate_template()


@api_view(["POST"])
@MiddlewareAutentication("general_master_country_import")
@transaction.atomic
def country_import_view(request):
    """
    Importa países desde un archivo Excel con validaciones masivas.
    """
    headers = ["Código", "Nombre", "Abreviación", "Estado"]
    handler = ExcelMasterHandler(Country, headers, "paises", request.user.id)

    # El import necesita un mapeo de { 'TítuloExcel/LlaveInterna': 'CampoModelo' }
    field_mapping = {
        "Código": "code",
        "Nombre": "name",
        "Abreviación": "abbreviation",
        "status_id": "status_id",
    }
    return handler.import_data(
        request, validate_country_import_row, field_mapping
    )
