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
from ..models import Group
from ..serializers import GroupSerializer


@extend_schema(request=None, responses={200: GroupSerializer(many=True)})
@MiddlewareAutentication("access_group_get")
@api_view(["POST"])
def group_get_view(request):
    status_filter = request.data.get("status", None)
    page = int(request.data.get("page", 1))
    page_size = min(int(request.data.get("page_size", 10)), 200)

    qs = Group.objects.exclude(status_id=STATUS_ANULADO)
    if status_filter == "activo":
        qs = Group.objects.filter(status_id=STATUS_ACTIVO)
    elif status_filter == "inactivo":
        qs = Group.objects.filter(status_id=STATUS_INACTIVO)
    elif status_filter == "anulado":
        qs = Group.objects.filter(status_id=STATUS_ANULADO)

    qs = qs.order_by("name")
    total = qs.count()
    start = (page - 1) * page_size
    end = start + page_size
    serializer = GroupSerializer(qs[start:end], many=True)
    return succescall(
        {
            "results": serializer.data,
            "total": total,
            "page": page,
            "page_size": page_size,
            "pages": (total + page_size - 1) // page_size,
        },
        "Lista de grupos obtenida correctamente",
    )


@extend_schema(request=None, responses={200: GroupSerializer(many=True)})
@api_view(["POST"])
@MiddlewareAutentication("access_group_select")
def group_select_view(request):
    groups = Group.objects.filter(
        status_id=STATUS_ACTIVO).order_by("name")
    serializer = GroupSerializer(groups, many=True)
    return succescall(serializer.data, "Grupos activos obtenidos")


@extend_schema(request=GroupSerializer, responses={201: GroupSerializer})
@api_view(["POST"])
@MiddlewareAutentication("access_group_create")
def group_create_view(request):
    name = str(request.data.get("name", "")).strip().upper()
    exists = Group.objects.filter(
        name__iexact=name,
        status_id__in=[STATUS_ACTIVO, STATUS_INACTIVO],
    ).exists()
    if exists:
        return errorcall(
            "Ya existe un grupo con ese nombre",
            status.HTTP_400_BAD_REQUEST,
        )
    mutable_data = request.data.copy()
    mutable_data["name"] = name
    serializer = GroupSerializer(data=mutable_data)
    if serializer.is_valid():
        serializer.save(
            key_user_created_id=request.user.id,
            key_user_updated_id=request.user.id,
            status_id=STATUS_ACTIVO,
        )
        return succescall(serializer.data, "Grupo creado correctamente")
    return errorcall(serializer.errors, status.HTTP_400_BAD_REQUEST)


@extend_schema(request=GroupSerializer, responses={200: GroupSerializer})
@api_view(["PATCH"])
@MiddlewareAutentication("access_group_update")
def group_update_view(request):
    pk = request.data.get("id")
    group = Group.objects.filter(pk=pk).first()
    if not group:
        return errorcall("Grupo no encontrado", status.HTTP_404_NOT_FOUND)

    name = str(request.data.get("name", group.name)).strip().upper()
    exists = (
        Group.objects.filter(
            name__iexact=name,
            status_id__in=[STATUS_ACTIVO, STATUS_INACTIVO],
        )
        .exclude(pk=pk)
        .exists()
    )
    if exists:
        return errorcall(
            "Ya existe otro grupo con ese nombre",
            status.HTTP_400_BAD_REQUEST,
        )

    mutable_data = request.data.copy()
    mutable_data["name"] = name
    serializer = GroupSerializer(group, data=mutable_data, partial=True)
    if serializer.is_valid():
        serializer.save(key_user_updated_id=request.user.id)
        return succescall(serializer.data, "Grupo actualizado correctamente")
    return errorcall(serializer.errors, status.HTTP_400_BAD_REQUEST)


@extend_schema(request=None, responses={200: OpenApiTypes.STR})
@api_view(["PATCH"])
@MiddlewareAutentication("access_group_inactivate")
def group_inactivate_view(request):
    pks = request.data.get("ids", [])
    pk = request.data.get("id")
    if pk:
        pks.append(pk)
    if not pks:
        return errorcall("IDs no proporcionados", status.HTTP_400_BAD_REQUEST)
    items = Group.objects.filter(pk__in=pks)
    if not items.exists():
        return errorcall("Grupos no encontrados", status.HTTP_404_NOT_FOUND)
    with transaction.atomic():
        for item in items:
            item.status_id = STATUS_INACTIVO
            item.key_user_updated_id = request.user.id
            item.save()
    return succescall(
        None, f"{items.count()} grupos inactivados correctamente")


@extend_schema(request=None, responses={200: OpenApiTypes.STR})
@api_view(["PATCH"])
@MiddlewareAutentication("access_group_restore")
def group_restore_view(request):
    pks = request.data.get("ids", [])
    pk = request.data.get("id")
    if pk:
        pks.append(pk)
    if not pks:
        return errorcall("IDs no proporcionados", status.HTTP_400_BAD_REQUEST)
    items = Group.objects.filter(pk__in=pks)
    if not items.exists():
        return errorcall("Grupos no encontrados", status.HTTP_404_NOT_FOUND)
    with transaction.atomic():
        for item in items:
            item.status_id = STATUS_ACTIVO
            item.key_user_updated_id = request.user.id
            item.save()
    return succescall(
        None, f"{items.count()} grupos restaurados correctamente")


@extend_schema(request=None, responses={200: OpenApiTypes.STR})
@api_view(["PATCH"])
@MiddlewareAutentication("access_group_annul")
def group_annul_view(request):
    pks = request.data.get("ids", [])
    pk = request.data.get("id")
    if pk:
        pks.append(pk)
    if not pks:
        return errorcall("IDs no proporcionados", status.HTTP_400_BAD_REQUEST)
    items = Group.objects.filter(pk__in=pks)
    if not items.exists():
        return errorcall("Grupos no encontrados", status.HTTP_404_NOT_FOUND)
    with transaction.atomic():
        for item in items:
            item.status_id = STATUS_ANULADO
            item.key_user_updated_id = request.user.id
            item.save()
    return succescall(
        None, f"{items.count()} grupos anulados correctamente")
