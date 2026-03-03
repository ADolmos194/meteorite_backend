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
from ..models import Role
from ..serializers import RoleSerializer


@extend_schema(request=None, responses={200: RoleSerializer(many=True)})
@MiddlewareAutentication("access_role_get")
@api_view(["POST"])
def role_get_view(request):
    status_filter = request.data.get("status", None)
    page = int(request.data.get("page", 1))
    page_size = min(int(request.data.get("page_size", 10)), 200)

    qs = Role.objects.exclude(status_id=STATUS_ANULADO)
    if status_filter == "activo":
        qs = Role.objects.filter(status_id=STATUS_ACTIVO)
    elif status_filter == "inactivo":
        qs = Role.objects.filter(status_id=STATUS_INACTIVO)
    elif status_filter == "anulado":
        qs = Role.objects.filter(status_id=STATUS_ANULADO)

    qs = qs.order_by("name")
    total = qs.count()
    start = (page - 1) * page_size
    end = start + page_size
    serializer = RoleSerializer(qs[start:end], many=True)
    return succescall(
        {
            "results": serializer.data,
            "total": total,
            "page": page,
            "page_size": page_size,
            "pages": (total + page_size - 1) // page_size,
        },
        "Lista de roles obtenida correctamente",
    )


@extend_schema(request=None, responses={200: RoleSerializer(many=True)})
@api_view(["POST"])
@MiddlewareAutentication("access_role_select")
def role_select_view(request):
    roles = Role.objects.filter(
        status_id=STATUS_ACTIVO).order_by("name")
    serializer = RoleSerializer(roles, many=True)
    return succescall(serializer.data, "Roles activos obtenidos")


@extend_schema(request=RoleSerializer, responses={201: RoleSerializer})
@api_view(["POST"])
@MiddlewareAutentication("access_role_create")
def role_create_view(request):
    name = str(request.data.get("name", "")).strip().upper()
    exists = Role.objects.filter(
        name__iexact=name,
        status_id__in=[STATUS_ACTIVO, STATUS_INACTIVO],
    ).exists()
    if exists:
        return errorcall(
            "Ya existe un rol con ese nombre",
            status.HTTP_400_BAD_REQUEST,
        )
    mutable_data = request.data.copy()
    mutable_data["name"] = name
    serializer = RoleSerializer(data=mutable_data)
    if serializer.is_valid():
        serializer.save(
            key_user_created_id=request.user.id,
            key_user_updated_id=request.user.id,
            status_id=STATUS_ACTIVO,
        )
        return succescall(serializer.data, "Rol creado correctamente")
    return errorcall(serializer.errors, status.HTTP_400_BAD_REQUEST)


@extend_schema(request=RoleSerializer, responses={200: RoleSerializer})
@api_view(["PATCH"])
@MiddlewareAutentication("access_role_update")
def role_update_view(request):
    pk = request.data.get("id")
    role = Role.objects.filter(pk=pk).first()
    if not role:
        return errorcall("Rol no encontrado", status.HTTP_404_NOT_FOUND)

    name = str(request.data.get("name", role.name)).strip().upper()
    exists = (
        Role.objects.filter(
            name__iexact=name,
            status_id__in=[STATUS_ACTIVO, STATUS_INACTIVO],
        )
        .exclude(pk=pk)
        .exists()
    )
    if exists:
        return errorcall(
            "Ya existe otro rol con ese nombre",
            status.HTTP_400_BAD_REQUEST,
        )

    mutable_data = request.data.copy()
    mutable_data["name"] = name
    serializer = RoleSerializer(role, data=mutable_data, partial=True)
    if serializer.is_valid():
        serializer.save(key_user_updated_id=request.user.id)
        return succescall(serializer.data, "Rol actualizado correctamente")
    return errorcall(serializer.errors, status.HTTP_400_BAD_REQUEST)


@extend_schema(request=None, responses={200: OpenApiTypes.STR})
@api_view(["PATCH"])
@MiddlewareAutentication("access_role_inactivate")
def role_inactivate_view(request):
    pks = request.data.get("ids", [])
    pk = request.data.get("id")
    if pk:
        pks.append(pk)
    if not pks:
        return errorcall("IDs no proporcionados", status.HTTP_400_BAD_REQUEST)
    items = Role.objects.filter(pk__in=pks)
    if not items.exists():
        return errorcall("Roles no encontrados", status.HTTP_404_NOT_FOUND)
    with transaction.atomic():
        for item in items:
            item.status_id = STATUS_INACTIVO
            item.key_user_updated_id = request.user.id
            item.save()
    return succescall(None, f"{items.count()} roles inactivados correctamente")


@extend_schema(request=None, responses={200: OpenApiTypes.STR})
@api_view(["PATCH"])
@MiddlewareAutentication("access_role_restore")
def role_restore_view(request):
    pks = request.data.get("ids", [])
    pk = request.data.get("id")
    if pk:
        pks.append(pk)
    if not pks:
        return errorcall("IDs no proporcionados", status.HTTP_400_BAD_REQUEST)
    items = Role.objects.filter(pk__in=pks)
    if not items.exists():
        return errorcall("Roles no encontrados", status.HTTP_404_NOT_FOUND)
    with transaction.atomic():
        for item in items:
            item.status_id = STATUS_ACTIVO
            item.key_user_updated_id = request.user.id
            item.save()
    return succescall(
        None, f"{items.count()} roles restaurados correctamente")


@extend_schema(request=None, responses={200: OpenApiTypes.STR})
@api_view(["PATCH"])
@MiddlewareAutentication("access_role_annul")
def role_annul_view(request):
    pks = request.data.get("ids", [])
    pk = request.data.get("id")
    if pk:
        pks.append(pk)
    if not pks:
        return errorcall("IDs no proporcionados", status.HTTP_400_BAD_REQUEST)
    items = Role.objects.filter(pk__in=pks)
    if not items.exists():
        return errorcall("Roles no encontrados", status.HTTP_404_NOT_FOUND)
    with transaction.atomic():
        for item in items:
            item.status_id = STATUS_ANULADO
            item.key_user_updated_id = request.user.id
            item.save()
    return succescall(None, f"{items.count()} roles anulados correctamente")
