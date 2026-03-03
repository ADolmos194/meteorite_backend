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
from ..models import Permission
from ..serializers import PermissionSerializer


@extend_schema(request=None, responses={200: PermissionSerializer(many=True)})
@MiddlewareAutentication("access_permission_get")
@api_view(["POST"])
def permission_get_view(request):
    status_filter = request.data.get("status", None)
    page = int(request.data.get("page", 1))
    page_size = min(int(request.data.get("page_size", 10)), 200)

    qs = Permission.objects.exclude(status_id=STATUS_ANULADO)
    if status_filter == "activo":
        qs = Permission.objects.filter(status_id=STATUS_ACTIVO)
    elif status_filter == "inactivo":
        qs = Permission.objects.filter(status_id=STATUS_INACTIVO)
    elif status_filter == "anulado":
        qs = Permission.objects.filter(status_id=STATUS_ANULADO)

    qs = qs.order_by("name")
    total = qs.count()
    start = (page - 1) * page_size
    end = start + page_size
    serializer = PermissionSerializer(qs[start:end], many=True)
    return succescall(
        {
            "results": serializer.data,
            "total": total,
            "page": page,
            "page_size": page_size,
            "pages": (total + page_size - 1) // page_size,
        },
        "Lista de permisos obtenida correctamente",
    )


@extend_schema(
    request=None, responses={200: PermissionSerializer(many=True)})
@api_view(["POST"])
@MiddlewareAutentication("access_permission_select")
def permission_select_view(request):
    perms = Permission.objects.filter(
        status_id=STATUS_ACTIVO).order_by("name")
    serializer = PermissionSerializer(perms, many=True)
    return succescall(serializer.data, "Permisos activos obtenidos")


@extend_schema(
    request=PermissionSerializer, responses={201: PermissionSerializer})
@api_view(["POST"])
@MiddlewareAutentication("access_permission_create")
def permission_create_view(request):
    name = str(request.data.get("name", "")).strip()
    decorator_name = str(
        request.data.get("decorator_name", "")).strip()

    exists = Permission.objects.filter(
        decorator_name=decorator_name,
        status_id__in=[STATUS_ACTIVO, STATUS_INACTIVO],
    ).exists()
    if exists:
        return errorcall(
            "Ya existe un permiso con ese decorator_name",
            status.HTTP_400_BAD_REQUEST,
        )

    mutable_data = request.data.copy()
    mutable_data["name"] = name
    mutable_data["decorator_name"] = decorator_name
    serializer = PermissionSerializer(data=mutable_data)
    if serializer.is_valid():
        serializer.save(
            key_user_created_id=request.user.id,
            key_user_updated_id=request.user.id,
            status_id=STATUS_ACTIVO,
        )
        return succescall(serializer.data, "Permiso creado correctamente")
    return errorcall(serializer.errors, status.HTTP_400_BAD_REQUEST)


@extend_schema(
    request=PermissionSerializer, responses={200: PermissionSerializer})
@api_view(["PATCH"])
@MiddlewareAutentication("access_permission_update")
def permission_update_view(request):
    pk = request.data.get("id")
    perm = Permission.objects.filter(pk=pk).first()
    if not perm:
        return errorcall(
            "Permiso no encontrado", status.HTTP_404_NOT_FOUND)

    decorator_name = str(
        request.data.get("decorator_name", perm.decorator_name)).strip()
    exists = (
        Permission.objects.filter(
            decorator_name=decorator_name,
            status_id__in=[STATUS_ACTIVO, STATUS_INACTIVO],
        )
        .exclude(pk=pk)
        .exists()
    )
    if exists:
        return errorcall(
            "Ya existe otro permiso con ese decorator_name",
            status.HTTP_400_BAD_REQUEST,
        )

    mutable_data = request.data.copy()
    mutable_data["decorator_name"] = decorator_name
    serializer = PermissionSerializer(perm, data=mutable_data, partial=True)
    if serializer.is_valid():
        serializer.save(key_user_updated_id=request.user.id)
        return succescall(
            serializer.data, "Permiso actualizado correctamente")
    return errorcall(serializer.errors, status.HTTP_400_BAD_REQUEST)


@extend_schema(request=None, responses={200: OpenApiTypes.STR})
@api_view(["PATCH"])
@MiddlewareAutentication("access_permission_inactivate")
def permission_inactivate_view(request):
    pks = request.data.get("ids", [])
    pk = request.data.get("id")
    if pk:
        pks.append(pk)
    if not pks:
        return errorcall("IDs no proporcionados", status.HTTP_400_BAD_REQUEST)
    items = Permission.objects.filter(pk__in=pks)
    if not items.exists():
        return errorcall(
            "Permisos no encontrados", status.HTTP_404_NOT_FOUND)
    with transaction.atomic():
        for item in items:
            item.status_id = STATUS_INACTIVO
            item.key_user_updated_id = request.user.id
            item.save()
    return succescall(
        None, f"{items.count()} permisos inactivados correctamente")


@extend_schema(request=None, responses={200: OpenApiTypes.STR})
@api_view(["PATCH"])
@MiddlewareAutentication("access_permission_restore")
def permission_restore_view(request):
    pks = request.data.get("ids", [])
    pk = request.data.get("id")
    if pk:
        pks.append(pk)
    if not pks:
        return errorcall("IDs no proporcionados", status.HTTP_400_BAD_REQUEST)
    items = Permission.objects.filter(pk__in=pks)
    if not items.exists():
        return errorcall(
            "Permisos no encontrados", status.HTTP_404_NOT_FOUND)
    with transaction.atomic():
        for item in items:
            item.status_id = STATUS_ACTIVO
            item.key_user_updated_id = request.user.id
            item.save()
    return succescall(
        None, f"{items.count()} permisos restaurados correctamente")


@extend_schema(request=None, responses={200: OpenApiTypes.STR})
@api_view(["PATCH"])
@MiddlewareAutentication("access_permission_annul")
def permission_annul_view(request):
    pks = request.data.get("ids", [])
    pk = request.data.get("id")
    if pk:
        pks.append(pk)
    if not pks:
        return errorcall("IDs no proporcionados", status.HTTP_400_BAD_REQUEST)
    items = Permission.objects.filter(pk__in=pks)
    if not items.exists():
        return errorcall(
            "Permisos no encontrados", status.HTTP_404_NOT_FOUND)
    with transaction.atomic():
        for item in items:
            item.status_id = STATUS_ANULADO
            item.key_user_updated_id = request.user.id
            item.save()
    return succescall(
        None, f"{items.count()} permisos anulados correctamente")
