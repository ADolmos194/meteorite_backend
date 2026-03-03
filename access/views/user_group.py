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
from ..models import Group, UserGroup
from ..serializers import UserGroupSerializer


@extend_schema(request=None, responses={200: UserGroupSerializer(many=True)})
@MiddlewareAutentication("access_user_group_get")
@api_view(["POST"])
def user_group_get_view(request):
    user_id = request.data.get("user_id")
    group_id = request.data.get("group_id")
    page = int(request.data.get("page", 1))
    page_size = min(int(request.data.get("page_size", 10)), 200)

    qs = UserGroup.objects.exclude(
        status_id=STATUS_ANULADO).select_related("group")
    if user_id:
        qs = qs.filter(user_id=user_id)
    if group_id:
        qs = qs.filter(group_id=group_id)

    qs = qs.order_by("-created_at")
    total = qs.count()
    start = (page - 1) * page_size
    end = start + page_size
    serializer = UserGroupSerializer(qs[start:end], many=True)
    return succescall(
        {
            "results": serializer.data,
            "total": total,
            "page": page,
            "page_size": page_size,
            "pages": (total + page_size - 1) // page_size,
        },
        "Asignaciones usuario-grupo obtenidas",
    )


@extend_schema(request=None, responses={201: UserGroupSerializer})
@api_view(["POST"])
@MiddlewareAutentication("access_user_group_assign")
def user_group_assign_view(request):
    user_id = request.data.get("user_id")
    group_id = request.data.get("group_id")

    if not user_id or not group_id:
        return errorcall(
            "Se requieren user_id y group_id",
            status.HTTP_400_BAD_REQUEST)

    if not User.objects.filter(id=user_id).exists():
        return errorcall(
            "Usuario no encontrado", status.HTTP_404_NOT_FOUND)

    group = Group.objects.filter(pk=group_id).first()
    if not group:
        return errorcall("Grupo no encontrado", status.HTTP_404_NOT_FOUND)

    already = UserGroup.objects.filter(
        user_id=user_id,
        group_id=group_id,
    ).exclude(status_id=STATUS_ANULADO).exists()
    if already:
        return errorcall(
            "El usuario ya pertenece a este grupo",
            status.HTTP_400_BAD_REQUEST)

    instance = UserGroup.objects.create(
        user_id=user_id,
        group_id=group_id,
        key_user_created_id=request.user.id,
        key_user_updated_id=request.user.id,
        status_id=STATUS_ACTIVO,
    )
    serializer = UserGroupSerializer(instance)
    return succescall(
        serializer.data, "Grupo asignado al usuario correctamente")


@extend_schema(request=None, responses={200: OpenApiTypes.STR})
@api_view(["DELETE"])
@MiddlewareAutentication("access_user_group_remove")
def user_group_remove_view(request):
    pk = request.data.get("id")
    if not pk:
        return errorcall("ID no proporcionado", status.HTTP_400_BAD_REQUEST)
    instance = UserGroup.objects.filter(pk=pk).first()
    if not instance:
        return errorcall(
            "Asignación no encontrada", status.HTTP_404_NOT_FOUND)
    instance.delete()
    return succescall(None, "Grupo removido del usuario correctamente")
