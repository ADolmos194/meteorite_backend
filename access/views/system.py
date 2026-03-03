from django.db import transaction
from rest_framework import status
from rest_framework.decorators import api_view
from drf_spectacular.utils import extend_schema, OpenApiTypes

from config.utils import (
    STATUS_ACTIVO,
    STATUS_ANULADO,
    STATUS_INACTIVO,
    MiddlewareAutentication,
    errorcall,
    succescall,
)
from ..models import System
from ..serializers import SystemSerializer


@extend_schema(request=None, responses={200: SystemSerializer(many=True)})
@MiddlewareAutentication("access_system_get")
@api_view(["POST"])
def system_get_view(request):
    status_filter = request.data.get("status", None)
    page = int(request.data.get("page", 1))
    page_size = min(int(request.data.get("page_size", 10)), 200)

    qs = System.objects.exclude(status_id=STATUS_ANULADO)
    if status_filter == "activo":
        qs = System.objects.filter(status_id=STATUS_ACTIVO)
    elif status_filter == "inactivo":
        qs = System.objects.filter(status_id=STATUS_INACTIVO)
    elif status_filter == "anulado":
        qs = System.objects.filter(status_id=STATUS_ANULADO)

    qs = qs.order_by("name")
    total = qs.count()
    start = (page - 1) * page_size
    end = start + page_size
    serializer = SystemSerializer(qs[start:end], many=True)
    return succescall(
        {
            "results": serializer.data,
            "total": total,
            "page": page,
            "page_size": page_size,
            "pages": (total + page_size - 1) // page_size,
        },
        "Lista de sistemas obtenida correctamente",
    )


@extend_schema(request=None, responses={200: SystemSerializer(many=True)})
@api_view(["POST"])
@MiddlewareAutentication("access_system_select")
def system_select_view(request):
    systems = System.objects.filter(
        status_id=STATUS_ACTIVO).order_by("name")
    serializer = SystemSerializer(systems, many=True)
    return succescall(serializer.data, "Sistemas activos obtenidos")


@extend_schema(request=SystemSerializer, responses={201: SystemSerializer})
@api_view(["POST"])
@MiddlewareAutentication("access_system_create")
def system_create_view(request):
    name = str(request.data.get("name", "")).strip().upper()
    exists = System.objects.filter(
        name__iexact=name,
        status_id__in=[STATUS_ACTIVO, STATUS_INACTIVO],
    ).exists()
    if exists:
        return errorcall(
            "Ya existe un sistema con ese nombre",
            status.HTTP_400_BAD_REQUEST,
        )
    mutable_data = request.data.copy()
    mutable_data["name"] = name
    serializer = SystemSerializer(data=mutable_data)
    if serializer.is_valid():
        serializer.save(
            key_user_created_id=request.user.id,
            key_user_updated_id=request.user.id,
            status_id=STATUS_ACTIVO,
        )
        return succescall(serializer.data, "Sistema creado correctamente")
    return errorcall(serializer.errors, status.HTTP_400_BAD_REQUEST)


@extend_schema(request=SystemSerializer, responses={200: SystemSerializer})
@api_view(["PATCH"])
@MiddlewareAutentication("access_system_update")
def system_update_view(request):
    pk = request.data.get("id")
    system = System.objects.filter(pk=pk).first()
    if not system:
        return errorcall("Sistema no encontrado", status.HTTP_404_NOT_FOUND)

    name = str(request.data.get("name", system.name)).strip().upper()
    exists = (
        System.objects.filter(
            name__iexact=name,
            status_id__in=[STATUS_ACTIVO, STATUS_INACTIVO],
        )
        .exclude(pk=pk)
        .exists()
    )
    if exists:
        return errorcall(
            "Ya existe otro sistema con ese nombre",
            status.HTTP_400_BAD_REQUEST,
        )

    mutable_data = request.data.copy()
    mutable_data["name"] = name
    serializer = SystemSerializer(system, data=mutable_data, partial=True)
    if serializer.is_valid():
        serializer.save(key_user_updated_id=request.user.id)
        return succescall(serializer.data, "Sistema actualizado correctamente")
    return errorcall(serializer.errors, status.HTTP_400_BAD_REQUEST)


@extend_schema(request=None, responses={200: OpenApiTypes.STR})
@api_view(["PATCH"])
@MiddlewareAutentication("access_system_inactivate")
def system_inactivate_view(request):
    pks = request.data.get("ids", [])
    pk = request.data.get("id")
    if pk:
        pks.append(pk)
    if not pks:
        return errorcall("IDs no proporcionados", status.HTTP_400_BAD_REQUEST)
    items = System.objects.filter(pk__in=pks)
    if not items.exists():
        return errorcall("Sistemas no encontrados", status.HTTP_404_NOT_FOUND)
    with transaction.atomic():
        for item in items:
            item.status_id = STATUS_INACTIVO
            item.key_user_updated_id = request.user.id
            item.save()
    return succescall(
        None, f"{items.count()} sistemas inactivados correctamente")


@extend_schema(request=None, responses={200: OpenApiTypes.STR})
@api_view(["PATCH"])
@MiddlewareAutentication("access_system_restore")
def system_restore_view(request):
    pks = request.data.get("ids", [])
    pk = request.data.get("id")
    if pk:
        pks.append(pk)
    if not pks:
        return errorcall("IDs no proporcionados", status.HTTP_400_BAD_REQUEST)
    items = System.objects.filter(pk__in=pks)
    if not items.exists():
        return errorcall("Sistemas no encontrados", status.HTTP_404_NOT_FOUND)
    with transaction.atomic():
        for item in items:
            item.status_id = STATUS_ACTIVO
            item.key_user_updated_id = request.user.id
            item.save()
    return succescall(
        None, f"{items.count()} sistemas restaurados correctamente")


@extend_schema(request=None, responses={200: OpenApiTypes.STR})
@api_view(["PATCH"])
@MiddlewareAutentication("access_system_annul")
def system_annul_view(request):
    pks = request.data.get("ids", [])
    pk = request.data.get("id")
    if pk:
        pks.append(pk)
    if not pks:
        return errorcall("IDs no proporcionados", status.HTTP_400_BAD_REQUEST)
    items = System.objects.filter(pk__in=pks)
    if not items.exists():
        return errorcall("Sistemas no encontrados", status.HTTP_404_NOT_FOUND)
    with transaction.atomic():
        for item in items:
            item.status_id = STATUS_ANULADO
            item.key_user_updated_id = request.user.id
            item.save()
    return succescall(None, f"{items.count()} sistemas anulados correctamente")
