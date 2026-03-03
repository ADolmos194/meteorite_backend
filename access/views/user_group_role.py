from rest_framework import status
from rest_framework.decorators import api_view
from drf_spectacular.utils import extend_schema, OpenApiTypes

from auth.models import User
from config.utils import (
    STATUS_ACTIVO,
    STATUS_ANULADO,
    MiddlewareAutentication,
    errorcall,
    succescall,
)
from ..models import Group, Role, UserGroupRole
from ..serializers import UserGroupRoleSerializer


@extend_schema(
    request=None, responses={200: UserGroupRoleSerializer(many=True)})
@MiddlewareAutentication("access_user_group_role_get")
@api_view(["POST"])
def user_group_role_get_view(request):
    user_id = request.data.get("user_id")
    group_id = request.data.get("group_id")
    page = int(request.data.get("page", 1))
    page_size = min(int(request.data.get("page_size", 10)), 200)

    qs = UserGroupRole.objects.exclude(
        status_id=STATUS_ANULADO).select_related("group", "role")
    if user_id:
        qs = qs.filter(user_id=user_id)
    if group_id:
        qs = qs.filter(group_id=group_id)

    qs = qs.order_by("-created_at")
    total = qs.count()
    start = (page - 1) * page_size
    end = start + page_size
    serializer = UserGroupRoleSerializer(qs[start:end], many=True)
    return succescall(
        {
            "results": serializer.data,
            "total": total,
            "page": page,
            "page_size": page_size,
            "pages": (total + page_size - 1) // page_size,
        },
        "Asignaciones usuario-grupo-rol obtenidas",
    )


@extend_schema(request=None, responses={201: UserGroupRoleSerializer})
@api_view(["POST"])
@MiddlewareAutentication("access_user_group_role_assign")
def user_group_role_assign_view(request):
    user_id = request.data.get("user_id")
    group_id = request.data.get("group_id")
    role_id = request.data.get("role_id")

    if not user_id or not group_id or not role_id:
        return errorcall(
            "Se requieren user_id, group_id y role_id",
            status.HTTP_400_BAD_REQUEST)

    if not User.objects.filter(id=user_id).exists():
        return errorcall("Usuario no encontrado", status.HTTP_404_NOT_FOUND)
    if not Group.objects.filter(pk=group_id).exists():
        return errorcall("Grupo no encontrado", status.HTTP_404_NOT_FOUND)
    if not Role.objects.filter(pk=role_id).exists():
        return errorcall("Rol no encontrado", status.HTTP_404_NOT_FOUND)

    already = UserGroupRole.objects.filter(
        user_id=user_id,
        group_id=group_id,
        role_id=role_id,
    ).exclude(status_id=STATUS_ANULADO).exists()
    if already:
        return errorcall(
            "El usuario ya tiene este rol en este grupo",
            status.HTTP_400_BAD_REQUEST)

    instance = UserGroupRole.objects.create(
        user_id=user_id,
        group_id=group_id,
        role_id=role_id,
        key_user_created_id=request.user.id,
        key_user_updated_id=request.user.id,
        status_id=STATUS_ACTIVO,
    )
    serializer = UserGroupRoleSerializer(instance)
    return succescall(
        serializer.data,
        "Rol asignado al usuario en el grupo correctamente")


@extend_schema(request=None, responses={200: OpenApiTypes.STR})
@api_view(["DELETE"])
@MiddlewareAutentication("access_user_group_role_remove")
def user_group_role_remove_view(request):
    pk = request.data.get("id")
    if not pk:
        return errorcall("ID no proporcionado", status.HTTP_400_BAD_REQUEST)
    instance = UserGroupRole.objects.filter(pk=pk).first()
    if not instance:
        return errorcall(
            "Asignación no encontrada", status.HTTP_404_NOT_FOUND)
    instance.delete()
    return succescall(
        None, "Rol removido del usuario en el grupo correctamente")
