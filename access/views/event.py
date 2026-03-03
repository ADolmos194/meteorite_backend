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
from ..models import Event
from ..serializers import EventSerializer


@extend_schema(request=None, responses={200: EventSerializer(many=True)})
@MiddlewareAutentication("access_event_get")
@api_view(["POST"])
def event_get_view(request):
    status_filter = request.data.get("status", None)
    page = int(request.data.get("page", 1))
    page_size = min(int(request.data.get("page_size", 10)), 200)

    qs = Event.objects.exclude(status_id=STATUS_ANULADO)
    if status_filter == "activo":
        qs = Event.objects.filter(status_id=STATUS_ACTIVO)
    elif status_filter == "inactivo":
        qs = Event.objects.filter(status_id=STATUS_INACTIVO)
    elif status_filter == "anulado":
        qs = Event.objects.filter(status_id=STATUS_ANULADO)

    qs = qs.order_by("name")
    total = qs.count()
    start = (page - 1) * page_size
    end = start + page_size
    serializer = EventSerializer(qs[start:end], many=True)
    return succescall(
        {
            "results": serializer.data,
            "total": total,
            "page": page,
            "page_size": page_size,
            "pages": (total + page_size - 1) // page_size,
        },
        "Lista de eventos obtenida correctamente",
    )


@extend_schema(request=None, responses={200: EventSerializer(many=True)})
@api_view(["POST"])
@MiddlewareAutentication("access_event_select")
def event_select_view(request):
    events = Event.objects.filter(
        status_id=STATUS_ACTIVO).order_by("name")
    serializer = EventSerializer(events, many=True)
    return succescall(serializer.data, "Eventos activos obtenidos")


@extend_schema(request=EventSerializer, responses={201: EventSerializer})
@api_view(["POST"])
@MiddlewareAutentication("access_event_create")
def event_create_view(request):
    name = str(request.data.get("name", "")).strip().upper()
    exists = Event.objects.filter(
        name__iexact=name,
        status_id__in=[STATUS_ACTIVO, STATUS_INACTIVO],
    ).exists()
    if exists:
        return errorcall(
            "Ya existe un evento con ese nombre",
            status.HTTP_400_BAD_REQUEST,
        )
    mutable_data = request.data.copy()
    mutable_data["name"] = name
    serializer = EventSerializer(data=mutable_data)
    if serializer.is_valid():
        serializer.save(
            key_user_created_id=request.user.id,
            key_user_updated_id=request.user.id,
            status_id=STATUS_ACTIVO,
        )
        return succescall(serializer.data, "Evento creado correctamente")
    return errorcall(serializer.errors, status.HTTP_400_BAD_REQUEST)


@extend_schema(request=EventSerializer, responses={200: EventSerializer})
@api_view(["PATCH"])
@MiddlewareAutentication("access_event_update")
def event_update_view(request):
    pk = request.data.get("id")
    event = Event.objects.filter(pk=pk).first()
    if not event:
        return errorcall("Evento no encontrado", status.HTTP_404_NOT_FOUND)

    name = str(request.data.get("name", event.name)).strip().upper()
    exists = (
        Event.objects.filter(
            name__iexact=name,
            status_id__in=[STATUS_ACTIVO, STATUS_INACTIVO],
        )
        .exclude(pk=pk)
        .exists()
    )
    if exists:
        return errorcall(
            "Ya existe otro evento con ese nombre",
            status.HTTP_400_BAD_REQUEST,
        )

    mutable_data = request.data.copy()
    mutable_data["name"] = name
    serializer = EventSerializer(event, data=mutable_data, partial=True)
    if serializer.is_valid():
        serializer.save(key_user_updated_id=request.user.id)
        return succescall(serializer.data, "Evento actualizado correctamente")
    return errorcall(serializer.errors, status.HTTP_400_BAD_REQUEST)


@extend_schema(request=None, responses={200: OpenApiTypes.STR})
@api_view(["PATCH"])
@MiddlewareAutentication("access_event_inactivate")
def event_inactivate_view(request):
    pks = request.data.get("ids", [])
    pk = request.data.get("id")
    if pk:
        pks.append(pk)
    if not pks:
        return errorcall("IDs no proporcionados", status.HTTP_400_BAD_REQUEST)
    items = Event.objects.filter(pk__in=pks)
    if not items.exists():
        return errorcall("Eventos no encontrados", status.HTTP_404_NOT_FOUND)
    with transaction.atomic():
        for item in items:
            item.status_id = STATUS_INACTIVO
            item.key_user_updated_id = request.user.id
            item.save()
    return succescall(
        None, f"{items.count()} eventos inactivados correctamente")


@extend_schema(request=None, responses={200: OpenApiTypes.STR})
@api_view(["PATCH"])
@MiddlewareAutentication("access_event_restore")
def event_restore_view(request):
    pks = request.data.get("ids", [])
    pk = request.data.get("id")
    if pk:
        pks.append(pk)
    if not pks:
        return errorcall("IDs no proporcionados", status.HTTP_400_BAD_REQUEST)
    items = Event.objects.filter(pk__in=pks)
    if not items.exists():
        return errorcall("Eventos no encontrados", status.HTTP_404_NOT_FOUND)
    with transaction.atomic():
        for item in items:
            item.status_id = STATUS_ACTIVO
            item.key_user_updated_id = request.user.id
            item.save()
    return succescall(
        None, f"{items.count()} eventos restaurados correctamente")


@extend_schema(request=None, responses={200: OpenApiTypes.STR})
@api_view(["PATCH"])
@MiddlewareAutentication("access_event_annul")
def event_annul_view(request):
    pks = request.data.get("ids", [])
    pk = request.data.get("id")
    if pk:
        pks.append(pk)
    if not pks:
        return errorcall("IDs no proporcionados", status.HTTP_400_BAD_REQUEST)
    items = Event.objects.filter(pk__in=pks)
    if not items.exists():
        return errorcall("Eventos no encontrados", status.HTTP_404_NOT_FOUND)
    with transaction.atomic():
        for item in items:
            item.status_id = STATUS_ANULADO
            item.key_user_updated_id = request.user.id
            item.save()
    return succescall(
        None, f"{items.count()} eventos anulados correctamente")
