from rest_framework import status
from rest_framework.decorators import api_view
from drf_spectacular.utils import extend_schema, OpenApiTypes

from config.utils import (
    STATUS_ACTIVO,
    STATUS_ANULADO,
    MiddlewareAutentication,
    errorcall,
    succescall,
)
from ..models import Permission, PermissionSystem, System
from ..serializers import PermissionSystemSerializer


@extend_schema(
    request=None, responses={200: PermissionSystemSerializer(many=True)})
@MiddlewareAutentication("access_permission_system_get")
@api_view(["POST"])
def permission_system_get_view(request):
    system_id = request.data.get("system_id")
    permission_id = request.data.get("permission_id")
    page = int(request.data.get("page", 1))
    page_size = min(int(request.data.get("page_size", 10)), 200)

    qs = PermissionSystem.objects.exclude(
        status_id=STATUS_ANULADO).select_related("permission", "system")
    if system_id:
        qs = qs.filter(system_id=system_id)
    if permission_id:
        qs = qs.filter(permission_id=permission_id)

    qs = qs.order_by("permission__name")
    total = qs.count()
    start = (page - 1) * page_size
    end = start + page_size
    serializer = PermissionSystemSerializer(qs[start:end], many=True)
    return succescall(
        {
            "results": serializer.data,
            "total": total,
            "page": page,
            "page_size": page_size,
            "pages": (total + page_size - 1) // page_size,
        },
        "Permisos del sistema obtenidos correctamente",
    )


@extend_schema(request=None, responses={201: PermissionSystemSerializer})
@api_view(["POST"])
@MiddlewareAutentication("access_permission_system_assign")
def permission_system_assign_view(request):
    permission_id = request.data.get("permission_id")
    system_id = request.data.get("system_id")

    if not permission_id or not system_id:
        return errorcall(
            "Se requieren permission_id y system_id",
            status.HTTP_400_BAD_REQUEST)

    if not Permission.objects.filter(pk=permission_id).exists():
        return errorcall(
            "Permiso no encontrado", status.HTTP_404_NOT_FOUND)
    if not System.objects.filter(pk=system_id).exists():
        return errorcall("Sistema no encontrado", status.HTTP_404_NOT_FOUND)

    already = PermissionSystem.objects.filter(
        permission_id=permission_id,
        system_id=system_id,
    ).exclude(status_id=STATUS_ANULADO).exists()
    if already:
        return errorcall(
            "Este permiso ya está asignado al sistema",
            status.HTTP_400_BAD_REQUEST)

    instance = PermissionSystem.objects.create(
        permission_id=permission_id,
        system_id=system_id,
        key_user_created_id=request.user.id,
        key_user_updated_id=request.user.id,
        status_id=STATUS_ACTIVO,
    )
    serializer = PermissionSystemSerializer(instance)
    return succescall(
        serializer.data, "Permiso asignado al sistema correctamente")


@extend_schema(request=None, responses={200: OpenApiTypes.STR})
@api_view(["DELETE"])
@MiddlewareAutentication("access_permission_system_remove")
def permission_system_remove_view(request):
    pk = request.data.get("id")
    if not pk:
        return errorcall("ID no proporcionado", status.HTTP_400_BAD_REQUEST)
    instance = PermissionSystem.objects.filter(pk=pk).first()
    if not instance:
        return errorcall(
            "Asignación no encontrada", status.HTTP_404_NOT_FOUND)
    instance.delete()
    return succescall(None, "Permiso removido del sistema correctamente")
