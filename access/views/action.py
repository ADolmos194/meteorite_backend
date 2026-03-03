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
from ..models import Action
from ..serializers import ActionSerializer


@extend_schema(request=None, responses={200: ActionSerializer(many=True)})
@MiddlewareAutentication("access_action_get")
@api_view(["POST"])
def action_get_view(request):
    status_filter = request.data.get("status", None)
    page = int(request.data.get("page", 1))
    page_size = min(int(request.data.get("page_size", 10)), 200)

    qs = Action.objects.exclude(status_id=STATUS_ANULADO)
    if status_filter == "activo":
        qs = Action.objects.filter(status_id=STATUS_ACTIVO)
    elif status_filter == "inactivo":
        qs = Action.objects.filter(status_id=STATUS_INACTIVO)
    elif status_filter == "anulado":
        qs = Action.objects.filter(status_id=STATUS_ANULADO)

    qs = qs.order_by("name")
    total = qs.count()
    start = (page - 1) * page_size
    end = start + page_size
    serializer = ActionSerializer(qs[start:end], many=True)
    return succescall(
        {
            "results": serializer.data,
            "total": total,
            "page": page,
            "page_size": page_size,
            "pages": (total + page_size - 1) // page_size,
        },
        "Lista de acciones obtenida correctamente",
    )


@extend_schema(request=None, responses={200: ActionSerializer(many=True)})
@api_view(["POST"])
@MiddlewareAutentication("access_action_select")
def action_select_view(request):
    actions = Action.objects.filter(
        status_id=STATUS_ACTIVO).order_by("name")
    serializer = ActionSerializer(actions, many=True)
    return succescall(serializer.data, "Acciones activas obtenidas")


@extend_schema(request=ActionSerializer, responses={201: ActionSerializer})
@api_view(["POST"])
@MiddlewareAutentication("access_action_create")
def action_create_view(request):
    name = str(request.data.get("name", "")).strip().upper()
    exists = Action.objects.filter(
        name__iexact=name,
        status_id__in=[STATUS_ACTIVO, STATUS_INACTIVO],
    ).exists()
    if exists:
        return errorcall(
            "Ya existe una acción con ese nombre",
            status.HTTP_400_BAD_REQUEST,
        )
    mutable_data = request.data.copy()
    mutable_data["name"] = name
    serializer = ActionSerializer(data=mutable_data)
    if serializer.is_valid():
        serializer.save(
            key_user_created_id=request.user.id,
            key_user_updated_id=request.user.id,
            status_id=STATUS_ACTIVO,
        )
        return succescall(serializer.data, "Acción creada correctamente")
    return errorcall(serializer.errors, status.HTTP_400_BAD_REQUEST)


@extend_schema(request=ActionSerializer, responses={200: ActionSerializer})
@api_view(["PATCH"])
@MiddlewareAutentication("access_action_update")
def action_update_view(request):
    pk = request.data.get("id")
    action = Action.objects.filter(pk=pk).first()
    if not action:
        return errorcall("Acción no encontrada", status.HTTP_404_NOT_FOUND)

    name = str(request.data.get("name", action.name)).strip().upper()
    exists = (
        Action.objects.filter(
            name__iexact=name,
            status_id__in=[STATUS_ACTIVO, STATUS_INACTIVO],
        )
        .exclude(pk=pk)
        .exists()
    )
    if exists:
        return errorcall(
            "Ya existe otra acción con ese nombre",
            status.HTTP_400_BAD_REQUEST,
        )

    mutable_data = request.data.copy()
    mutable_data["name"] = name
    serializer = ActionSerializer(action, data=mutable_data, partial=True)
    if serializer.is_valid():
        serializer.save(key_user_updated_id=request.user.id)
        return succescall(
            serializer.data, "Acción actualizada correctamente")
    return errorcall(serializer.errors, status.HTTP_400_BAD_REQUEST)


@extend_schema(request=None, responses={200: OpenApiTypes.STR})
@api_view(["PATCH"])
@MiddlewareAutentication("access_action_inactivate")
def action_inactivate_view(request):
    pks = request.data.get("ids", [])
    pk = request.data.get("id")
    if pk:
        pks.append(pk)
    if not pks:
        return errorcall("IDs no proporcionados", status.HTTP_400_BAD_REQUEST)
    items = Action.objects.filter(pk__in=pks)
    if not items.exists():
        return errorcall("Acciones no encontradas", status.HTTP_404_NOT_FOUND)
    with transaction.atomic():
        for item in items:
            item.status_id = STATUS_INACTIVO
            item.key_user_updated_id = request.user.id
            item.save()
    return succescall(
        None, f"{items.count()} acciones inactivadas correctamente")


@extend_schema(request=None, responses={200: OpenApiTypes.STR})
@api_view(["PATCH"])
@MiddlewareAutentication("access_action_restore")
def action_restore_view(request):
    pks = request.data.get("ids", [])
    pk = request.data.get("id")
    if pk:
        pks.append(pk)
    if not pks:
        return errorcall("IDs no proporcionados", status.HTTP_400_BAD_REQUEST)
    items = Action.objects.filter(pk__in=pks)
    if not items.exists():
        return errorcall("Acciones no encontradas", status.HTTP_404_NOT_FOUND)
    with transaction.atomic():
        for item in items:
            item.status_id = STATUS_ACTIVO
            item.key_user_updated_id = request.user.id
            item.save()
    return succescall(
        None, f"{items.count()} acciones restauradas correctamente")


@extend_schema(request=None, responses={200: OpenApiTypes.STR})
@api_view(["PATCH"])
@MiddlewareAutentication("access_action_annul")
def action_annul_view(request):
    pks = request.data.get("ids", [])
    pk = request.data.get("id")
    if pk:
        pks.append(pk)
    if not pks:
        return errorcall("IDs no proporcionados", status.HTTP_400_BAD_REQUEST)
    items = Action.objects.filter(pk__in=pks)
    if not items.exists():
        return errorcall("Acciones no encontradas", status.HTTP_404_NOT_FOUND)
    with transaction.atomic():
        for item in items:
            item.status_id = STATUS_ANULADO
            item.key_user_updated_id = request.user.id
            item.save()
    return succescall(
        None, f"{items.count()} acciones anuladas correctamente")
