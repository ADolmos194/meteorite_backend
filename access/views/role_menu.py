from django.db import IntegrityError
from rest_framework import status as drf_status
from rest_framework.decorators import api_view
from drf_spectacular.utils import extend_schema, OpenApiTypes

from config.utils import (
    STATUS_ACTIVO,
    STATUS_ANULADO,
    MiddlewareAutentication,
    errorcall,
    succescall,
    warningcall,
)
from ..models import Menu, Role, RoleMenu
from ..serializers import RoleMenuSerializer


@extend_schema(
    request=None, responses={200: RoleMenuSerializer(many=True)})
@MiddlewareAutentication("access_role_menu_get")
@api_view(["POST"])
def role_menu_get_view(request):
    role_id = request.data.get("role_id")
    menu_id = request.data.get("menu_id")
    page = int(request.data.get("page", 1))
    page_size = min(int(request.data.get("page_size", 10)), 200)

    qs = RoleMenu.objects.exclude(
        status_id=STATUS_ANULADO).select_related("role", "menu")
    if role_id:
        qs = qs.filter(role_id=role_id)
    if menu_id:
        qs = qs.filter(menu_id=menu_id)

    qs = qs.order_by("menu__ordering", "menu__title")
    total = qs.count()
    start = (page - 1) * page_size
    end = start + page_size
    serializer = RoleMenuSerializer(qs[start:end], many=True)
    return succescall(
        {
            "results": serializer.data,
            "total": total,
            "page": page,
            "page_size": page_size,
            "pages": (total + page_size - 1) // page_size,
        },
        "Menús del rol obtenidos correctamente",
    )


@extend_schema(request=None, responses={201: RoleMenuSerializer})
@api_view(["POST"])
@MiddlewareAutentication("access_role_menu_assign")
def role_menu_assign_view(request):
    role_id = request.data.get("role_id")
    menu_id = request.data.get("menu_id")

    if not role_id or not menu_id:
        return errorcall(
            "Se requieren role_id y menu_id",
            drf_status.HTTP_400_BAD_REQUEST)

    if not Role.objects.filter(pk=role_id).exists():
        return errorcall("Rol no encontrado", drf_status.HTTP_404_NOT_FOUND)
    if not Menu.objects.filter(pk=menu_id).exists():
        return errorcall("Menú no encontrado", drf_status.HTTP_404_NOT_FOUND)

    try:
        instance = RoleMenu.objects.create(
            role_id=role_id,
            menu_id=menu_id,
            key_user_created_id=request.user.id,
            key_user_updated_id=request.user.id,
            status_id=STATUS_ACTIVO,
        )
    except IntegrityError:
        return warningcall("Este menú ya está asignado a este rol")

    serializer = RoleMenuSerializer(instance)
    return succescall(
        serializer.data, "Menú asignado al rol correctamente")


@extend_schema(request=None, responses={200: OpenApiTypes.STR})
@api_view(["DELETE"])
@MiddlewareAutentication("access_role_menu_remove")
def role_menu_remove_view(request):
    pk = request.data.get("id")
    if not pk:
        return errorcall(
            "ID no proporcionado", drf_status.HTTP_400_BAD_REQUEST)
    instance = RoleMenu.objects.filter(pk=pk).first()
    if not instance:
        return errorcall(
            "Asignación no encontrada", drf_status.HTTP_404_NOT_FOUND)
    instance.delete()
    return succescall(None, "Menú removido del rol correctamente")
