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
from ..models import Role, UserRole
from ..serializers import UserRoleSerializer


@extend_schema(request=None, responses={200: UserRoleSerializer(many=True)})
@MiddlewareAutentication("access_user_role_get")
@api_view(["POST"])
def user_role_get_view(request):
    user_id = request.data.get("user_id")
    role_id = request.data.get("role_id")
    page = int(request.data.get("page", 1))
    page_size = min(int(request.data.get("page_size", 10)), 200)

    qs = UserRole.objects.exclude(
        status_id=STATUS_ANULADO).select_related("role")
    if user_id:
        qs = qs.filter(user_id=user_id)
    if role_id:
        qs = qs.filter(role_id=role_id)

    qs = qs.order_by("-created_at")
    total = qs.count()
    start = (page - 1) * page_size
    end = start + page_size
    serializer = UserRoleSerializer(qs[start:end], many=True)
    return succescall(
        {
            "results": serializer.data,
            "total": total,
            "page": page,
            "page_size": page_size,
            "pages": (total + page_size - 1) // page_size,
        },
        "Asignaciones usuario-rol obtenidas",
    )


@extend_schema(request=None, responses={201: UserRoleSerializer})
@api_view(["POST"])
@MiddlewareAutentication("access_user_role_assign")
def user_role_assign_view(request):
    user_id = request.data.get("user_id")
    role_id = request.data.get("role_id")

    if not user_id or not role_id:
        return errorcall(
            "Se requieren user_id y role_id",
            status.HTTP_400_BAD_REQUEST)

    if not User.objects.filter(id=user_id).exists():
        return errorcall(
            "Usuario no encontrado", status.HTTP_404_NOT_FOUND)

    role = Role.objects.filter(pk=role_id).first()
    if not role:
        return errorcall("Rol no encontrado", status.HTTP_404_NOT_FOUND)

    already = UserRole.objects.filter(
        user_id=user_id,
        role_id=role_id,
    ).exclude(status_id=STATUS_ANULADO).exists()
    if already:
        return errorcall(
            "El usuario ya tiene este rol asignado",
            status.HTTP_400_BAD_REQUEST)

    instance = UserRole.objects.create(
        user_id=user_id,
        role_id=role_id,
        key_user_created_id=request.user.id,
        key_user_updated_id=request.user.id,
        status_id=STATUS_ACTIVO,
    )
    serializer = UserRoleSerializer(instance)
    return succescall(serializer.data, "Rol asignado al usuario correctamente")


@extend_schema(request=None, responses={200: OpenApiTypes.STR})
@api_view(["DELETE"])
@MiddlewareAutentication("access_user_role_remove")
def user_role_remove_view(request):
    pk = request.data.get("id")
    if not pk:
        return errorcall("ID no proporcionado", status.HTTP_400_BAD_REQUEST)

    instance = UserRole.objects.filter(pk=pk).first()
    if not instance:
        return errorcall(
            "Asignación no encontrada", status.HTTP_404_NOT_FOUND)

    instance.delete()
    return succescall(None, "Rol removido del usuario correctamente")
