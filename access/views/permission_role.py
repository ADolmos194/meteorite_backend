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
from ..models import Permission, PermissionRole, Role
from ..serializers import PermissionRoleSerializer


@extend_schema(
    request=None, responses={200: PermissionRoleSerializer(many=True)})
@MiddlewareAutentication("access_permission_role_get")
@api_view(["POST"])
def permission_role_get_view(request):
    role_id = request.data.get("role_id")
    permission_id = request.data.get("permission_id")
    page = int(request.data.get("page", 1))
    page_size = min(int(request.data.get("page_size", 10)), 200)

    qs = PermissionRole.objects.exclude(
        status_id=STATUS_ANULADO).select_related("permission", "role")
    if role_id:
        qs = qs.filter(role_id=role_id)
    if permission_id:
        qs = qs.filter(permission_id=permission_id)

    qs = qs.order_by("permission__name")
    total = qs.count()
    start = (page - 1) * page_size
    end = start + page_size
    serializer = PermissionRoleSerializer(qs[start:end], many=True)
    return succescall(
        {
            "results": serializer.data,
            "total": total,
            "page": page,
            "page_size": page_size,
            "pages": (total + page_size - 1) // page_size,
        },
        "Permisos del rol obtenidos correctamente",
    )


@extend_schema(request=None, responses={201: PermissionRoleSerializer})
@api_view(["POST"])
@MiddlewareAutentication("access_permission_role_assign")
def permission_role_assign_view(request):
    permission_id = request.data.get("permission_id")
    role_id = request.data.get("role_id")

    if not permission_id or not role_id:
        return errorcall(
            "Se requieren permission_id y role_id",
            status.HTTP_400_BAD_REQUEST)

    if not Permission.objects.filter(pk=permission_id).exists():
        return errorcall(
            "Permiso no encontrado", status.HTTP_404_NOT_FOUND)
    if not Role.objects.filter(pk=role_id).exists():
        return errorcall("Rol no encontrado", status.HTTP_404_NOT_FOUND)

    already = PermissionRole.objects.filter(
        permission_id=permission_id,
        role_id=role_id,
    ).exclude(status_id=STATUS_ANULADO).exists()
    if already:
        return errorcall(
            "Este permiso ya está asignado al rol",
            status.HTTP_400_BAD_REQUEST)

    instance = PermissionRole.objects.create(
        permission_id=permission_id,
        role_id=role_id,
        key_user_created_id=request.user.id,
        key_user_updated_id=request.user.id,
        status_id=STATUS_ACTIVO,
    )
    serializer = PermissionRoleSerializer(instance)
    return succescall(
        serializer.data, "Permiso asignado al rol correctamente")


@extend_schema(request=None, responses={200: OpenApiTypes.STR})
@api_view(["DELETE"])
@MiddlewareAutentication("access_permission_role_remove")
def permission_role_remove_view(request):
    pk = request.data.get("id")
    if not pk:
        return errorcall("ID no proporcionado", status.HTTP_400_BAD_REQUEST)
    instance = PermissionRole.objects.filter(pk=pk).first()
    if not instance:
        return errorcall(
            "Asignación no encontrada", status.HTTP_404_NOT_FOUND)
    instance.delete()
    return succescall(None, "Permiso removido del rol correctamente")
