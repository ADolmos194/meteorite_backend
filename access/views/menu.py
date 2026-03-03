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
from access.utils import build_menu_tree
from ..models import Menu
from ..serializers import MenuSerializer


@extend_schema(request=None, responses={200: MenuSerializer(many=True)})
@MiddlewareAutentication("access_menu_get")
@api_view(["POST"])
def menu_get_view(request):
    status_filter = request.data.get("status", None)
    parent_id = request.data.get("parent", None)
    page = int(request.data.get("page", 1))
    page_size = min(int(request.data.get("page_size", 10)), 200)

    qs = Menu.objects.exclude(status_id=STATUS_ANULADO)
    if status_filter == "activo":
        qs = Menu.objects.filter(status_id=STATUS_ACTIVO)
    elif status_filter == "inactivo":
        qs = Menu.objects.filter(status_id=STATUS_INACTIVO)
    elif status_filter == "anulado":
        qs = Menu.objects.filter(status_id=STATUS_ANULADO)

    if parent_id:
        qs = qs.filter(parent_id=parent_id)

    qs = qs.order_by("ordering", "title")
    total = qs.count()
    start = (page - 1) * page_size
    end = start + page_size
    serializer = MenuSerializer(qs[start:end], many=True)
    return succescall(
        {
            "results": serializer.data,
            "total": total,
            "page": page,
            "page_size": page_size,
            "pages": (total + page_size - 1) // page_size,
        },
        "Lista de menús obtenida correctamente",
    )


@extend_schema(request=None, responses={200: OpenApiTypes.OBJECT})
@api_view(["GET"])
@MiddlewareAutentication("access_menu_tree")
def menu_tree_view(request):
    menus = list(Menu.objects.filter(
        status_id=STATUS_ACTIVO).order_by("ordering"))
    tree = build_menu_tree(menus)
    return succescall(tree, "Árbol de menús obtenido correctamente")


@extend_schema(request=None, responses={200: MenuSerializer(many=True)})
@api_view(["POST"])
@MiddlewareAutentication("access_menu_select")
def menu_select_view(request):
    menus = Menu.objects.filter(
        status_id=STATUS_ACTIVO).order_by("ordering", "title")
    serializer = MenuSerializer(menus, many=True)
    return succescall(serializer.data, "Menús activos obtenidos")


@extend_schema(request=MenuSerializer, responses={201: MenuSerializer})
@api_view(["POST"])
@MiddlewareAutentication("access_menu_create")
def menu_create_view(request):
    from django.db.models import Q
    title = str(request.data.get("title", "")).strip()
    parent_id = request.data.get("parent", None)

    exists = Menu.objects.filter(
        Q(title__iexact=title),
        parent_id=parent_id,
        status_id__in=[STATUS_ACTIVO, STATUS_INACTIVO],
    ).exists()
    if exists:
        return errorcall(
            "Ya existe un menú con ese título en este nivel",
            status.HTTP_400_BAD_REQUEST,
        )

    mutable_data = request.data.copy()
    mutable_data["title"] = title
    serializer = MenuSerializer(data=mutable_data)
    if serializer.is_valid():
        serializer.save(
            key_user_created_id=request.user.id,
            key_user_updated_id=request.user.id,
            status_id=STATUS_ACTIVO,
        )
        return succescall(serializer.data, "Menú creado correctamente")
    return errorcall(serializer.errors, status.HTTP_400_BAD_REQUEST)


@extend_schema(request=MenuSerializer, responses={200: MenuSerializer})
@api_view(["PATCH"])
@MiddlewareAutentication("access_menu_update")
def menu_update_view(request):
    from django.db.models import Q
    pk = request.data.get("id")
    menu = Menu.objects.filter(pk=pk).first()
    if not menu:
        return errorcall("Menú no encontrado", status.HTTP_404_NOT_FOUND)

    title = str(request.data.get("title", menu.title)).strip()
    parent_id = request.data.get("parent", menu.parent_id)
    exists = (
        Menu.objects.filter(
            Q(title__iexact=title),
            parent_id=parent_id,
            status_id__in=[STATUS_ACTIVO, STATUS_INACTIVO],
        )
        .exclude(pk=pk)
        .exists()
    )
    if exists:
        return errorcall(
            "Ya existe otro menú con ese título en este nivel",
            status.HTTP_400_BAD_REQUEST,
        )

    mutable_data = request.data.copy()
    mutable_data["title"] = title
    serializer = MenuSerializer(menu, data=mutable_data, partial=True)
    if serializer.is_valid():
        serializer.save(key_user_updated_id=request.user.id)
        return succescall(serializer.data, "Menú actualizado correctamente")
    return errorcall(serializer.errors, status.HTTP_400_BAD_REQUEST)


@extend_schema(request=None, responses={200: OpenApiTypes.STR})
@api_view(["PATCH"])
@MiddlewareAutentication("access_menu_inactivate")
def menu_inactivate_view(request):
    pks = request.data.get("ids", [])
    pk = request.data.get("id")
    if pk:
        pks.append(pk)
    if not pks:
        return errorcall("IDs no proporcionados", status.HTTP_400_BAD_REQUEST)

    items = Menu.objects.filter(pk__in=pks)
    if not items.exists():
        return errorcall("Menús no encontrados", status.HTTP_404_NOT_FOUND)

    with transaction.atomic():
        for item in items:
            item.status_id = STATUS_INACTIVO
            item.key_user_updated_id = request.user.id
            item.save()

    return succescall(None, f"{items.count()} menús inactivados correctamente")


@extend_schema(request=None, responses={200: OpenApiTypes.STR})
@api_view(["PATCH"])
@MiddlewareAutentication("access_menu_restore")
def menu_restore_view(request):
    pks = request.data.get("ids", [])
    pk = request.data.get("id")
    if pk:
        pks.append(pk)
    if not pks:
        return errorcall("IDs no proporcionados", status.HTTP_400_BAD_REQUEST)

    items = Menu.objects.filter(pk__in=pks)
    if not items.exists():
        return errorcall("Menús no encontrados", status.HTTP_404_NOT_FOUND)

    with transaction.atomic():
        for item in items:
            item.status_id = STATUS_ACTIVO
            item.key_user_updated_id = request.user.id
            item.save()

    return succescall(None, f"{items.count()} menús restaurados correctamente")


@extend_schema(request=None, responses={200: OpenApiTypes.STR})
@api_view(["PATCH"])
@MiddlewareAutentication("access_menu_annul")
def menu_annul_view(request):
    pks = request.data.get("ids", [])
    pk = request.data.get("id")
    if pk:
        pks.append(pk)
    if not pks:
        return errorcall("IDs no proporcionados", status.HTTP_400_BAD_REQUEST)

    items = Menu.objects.filter(pk__in=pks)
    if not items.exists():
        return errorcall("Menús no encontrados", status.HTTP_404_NOT_FOUND)

    with transaction.atomic():
        for item in items:
            item.status_id = STATUS_ANULADO
            item.key_user_updated_id = request.user.id
            item.save()

    return succescall(None, f"{items.count()} menús anulados correctamente")
