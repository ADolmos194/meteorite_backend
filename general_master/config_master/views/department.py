import copy
from django.db import transaction
from rest_framework import status
from rest_framework.decorators import api_view

from config.excel_handler import ExcelMasterHandler
from config.utils import (
    STATUS_ACTIVO,
    STATUS_ANULADO,
    STATUS_INACTIVO,
    MiddlewareAutentication,
    errorcall,
    succescall,
)

from audit.utils import (
    EVENT_ANNUL,
    EVENT_CREATE,
    EVENT_INACTIVATE,
    EVENT_RESTORE,
    EVENT_UPDATE,
    EVENT_IMPORT,
    EVENT_MASS_ACTIVATE,
    EVENT_MASS_INACTIVATE,
    EVENT_MASS_ANNUL,
    save_audit_log,
)
from ..import_validators import validate_department_import_row
from ..models import Department
from ..serializers import DepartmentSerializer
from audit.models import AuditLog, AuditLogDetail
from audit.serializers import AuditLogSerializer, AuditLogDetailSerializer


@MiddlewareAutentication("general_master_department_get")
@api_view(["POST"])
def department_get_view(request):
    country_id = request.data.get("country")
    status_filter = request.data.get("status", None)
    page = int(request.data.get("page", 1))
    page_size = min(int(request.data.get("page_size", 10)), 200)

    qs = Department.objects.exclude(status_id=STATUS_ANULADO)
    if status_filter == "activo":
        qs = Department.objects.filter(status_id=STATUS_ACTIVO)
    elif status_filter == "inactivo":
        qs = Department.objects.filter(status_id=STATUS_INACTIVO)
    elif status_filter == "anulado":
        qs = Department.objects.filter(status_id=STATUS_ANULADO)

    if country_id:
        qs = qs.filter(key_country_id=country_id)

    qs = qs.order_by("-created_at")
    total = qs.count()
    start = (page - 1) * page_size
    end = start + page_size
    serializer = DepartmentSerializer(qs[start:end], many=True)
    return succescall(
        {
            "results": serializer.data,
            "total": total,
            "page": page,
            "page_size": page_size,
            "pages": (total + page_size - 1) // page_size,
        },
        "Lista de departamentos obtenida correctamente",
    )


@api_view(["POST"])
@MiddlewareAutentication("general_master_department_create")
def department_create_view(request):
    from django.db.models import Q
    code = str(request.data.get("code", "")).strip().upper()
    name = str(request.data.get("name", "")).strip().upper()
    abbreviation = str(request.data.get("abbreviation", "")).strip().upper()
    country_id = request.data.get("key_country")

    exists = Department.objects.filter(
        Q(code=code) | Q(name=name),
        key_country_id=country_id,
        status_id__in=[STATUS_ACTIVO, STATUS_INACTIVO],
    ).exists()

    if exists:
        return errorcall(
            "Ya existe un departamento con ese código o nombre en este país",
            status.HTTP_400_BAD_REQUEST,
        )

    mutable_data = request.data.copy()
    mutable_data["code"] = code
    mutable_data["name"] = name
    mutable_data["abbreviation"] = abbreviation

    serializer = DepartmentSerializer(data=mutable_data)
    if serializer.is_valid():
        instance = serializer.save(
            key_user_created_id=request.user.id,
            key_user_updated_id=request.user.id,
            status_id=STATUS_ACTIVO,
        )
        save_audit_log(instance, request.user.id, EVENT_CREATE)
        return succescall(serializer.data, "Departamento creado correctamente")
    return errorcall(serializer.errors, status.HTTP_400_BAD_REQUEST)


@api_view(["PATCH"])
@MiddlewareAutentication("general_master_department_update")
def department_update_view(request):
    from django.db.models import Q
    pk = request.data.get("id")
    dept = Department.objects.filter(pk=pk).first()
    if not dept:
        return errorcall("Departamento no encontrado", status.HTTP_404_NOT_FOUND)

    code = str(request.data.get("code", dept.code)).strip().upper()
    name = str(request.data.get("name", dept.name)).strip().upper()
    
    exists = (
        Department.objects.filter(
            Q(code=code) | Q(name=name),
            key_country_id=dept.key_country_id,
            status_id__in=[STATUS_ACTIVO, STATUS_INACTIVO],
        )
        .exclude(pk=pk)
        .exists()
    )

    if exists:
        return errorcall(
            "Ya existe otro departamento con ese código o nombre en este país",
            status.HTTP_400_BAD_REQUEST,
        )

    old_instance = copy.copy(dept)
    mutable_data = request.data.copy()
    mutable_data["code"] = code
    mutable_data["name"] = name

    serializer = DepartmentSerializer(dept, data=mutable_data, partial=True)
    if serializer.is_valid():
        instance = serializer.save(key_user_updated_id=request.user.id)
        save_audit_log(instance, request.user.id, EVENT_UPDATE, old_instance)
        return succescall(serializer.data, "Departamento actualizado correctamente")
    return errorcall(serializer.errors, status.HTTP_400_BAD_REQUEST)


@api_view(["PATCH"])
@MiddlewareAutentication("general_master_department_inactivate")
def department_inactivate_view(request):
    pks = request.data.get("ids", [])
    pk = request.data.get("id")
    if pk: pks.append(pk)
    
    if not pks:
        return errorcall("IDs no proporcionados", status.HTTP_400_BAD_REQUEST)

    is_mass = bool(request.data.get("ids", []))
    event_type = EVENT_MASS_INACTIVATE if is_mass else EVENT_INACTIVATE

    depts = Department.objects.filter(pk__in=pks)
    if not depts.exists():
        return errorcall("Departamentos no encontrados", status.HTTP_404_NOT_FOUND)

    count = 0
    with transaction.atomic():
        for dept in depts:
            dept.status_id = STATUS_INACTIVO
            dept.key_user_updated_id = request.user.id
            dept.save()
            save_audit_log(dept, request.user.id, event_type)
            count += 1
    
    return succescall(None, f"{count} departamentos inactivados correctamente")


@api_view(["PATCH"])
@MiddlewareAutentication("general_master_department_restore")
def department_restore_view(request):
    pks = request.data.get("ids", [])
    pk = request.data.get("id")
    if pk: pks.append(pk)
    
    if not pks:
        return errorcall("IDs no proporcionados", status.HTTP_400_BAD_REQUEST)

    is_mass = bool(request.data.get("ids", []))
    event_type = EVENT_MASS_ACTIVATE if is_mass else EVENT_RESTORE

    depts = Department.objects.filter(pk__in=pks)
    if not depts.exists():
        return errorcall("Departamentos no encontrados", status.HTTP_404_NOT_FOUND)

    count = 0
    with transaction.atomic():
        for dept in depts:
            dept.status_id = STATUS_ACTIVO
            dept.key_user_updated_id = request.user.id
            dept.save()
            save_audit_log(dept, request.user.id, event_type)
            count += 1

    return succescall(None, f"{count} departamentos restaurados correctamente")


@api_view(["PATCH"])
@MiddlewareAutentication("general_master_department_annul")
def department_annul_view(request):
    pks = request.data.get("ids", [])
    pk = request.data.get("id")
    if pk: pks.append(pk)
    
    if not pks:
        return errorcall("IDs no proporcionados", status.HTTP_400_BAD_REQUEST)

    is_mass = bool(request.data.get("ids", []))
    event_type = EVENT_MASS_ANNUL if is_mass else EVENT_ANNUL

    depts = Department.objects.filter(pk__in=pks)
    if not depts.exists():
        return errorcall("Departamentos no encontrados", status.HTTP_404_NOT_FOUND)

    count = 0
    with transaction.atomic():
        for dept in depts:
            dept.status_id = STATUS_ANULADO
            dept.key_user_updated_id = request.user.id
            dept.save()
            save_audit_log(dept, request.user.id, event_type)
            count += 1
    
    return succescall(None, f"{count} departamentos anulados correctamente")


@api_view(["POST"])
@MiddlewareAutentication("general_master_department_log")
def department_log_view(request):
    pk = request.data.get("id")
    if not pk:
        return errorcall("ID no proporcionado", status.HTTP_400_BAD_REQUEST)

    dept = Department.objects.filter(pk=pk).first()
    if not dept:
        return errorcall("Departamento no encontrado", status.HTTP_404_NOT_FOUND)

    logs = AuditLog.objects.filter(
        record_id=pk,
        name_table=Department._meta.db_table
    ).order_by("-created_at")
    serializer = AuditLogSerializer(logs, many=True)
    return succescall(serializer.data, "Logs del departamento obtenidos correctamente")


@api_view(["POST"])
@MiddlewareAutentication("general_master_department_log_detail")
def department_log_detail_view(request):
    pk = request.data.get("id")
    if not pk:
        return errorcall("ID no proporcionado", status.HTTP_400_BAD_REQUEST)

    log = AuditLog.objects.filter(pk=pk).first()
    if not log:
        return errorcall("Log no encontrado", status.HTTP_404_NOT_FOUND)

    details = AuditLogDetail.objects.filter(
        key_audit_log=log,
        key_audit_log__name_table=Department._meta.db_table
    )
    serializer = AuditLogDetailSerializer(details, many=True)
    return succescall(serializer.data, "Detalles del log obtenidos correctamente")


@api_view(["GET"])
@MiddlewareAutentication("general_master_department_export")
def department_export_view(request):
    depts = Department.objects.exclude(status_id=STATUS_ANULADO).order_by("key_country__name", "name")
    headers = ["CÓDIGO", "NOMBRE", "ABREVIACIÓN", "PAÍS", "ESTADO"]
    handler = ExcelMasterHandler(Department, headers, "departamentos", request.user.id)
    field_mapping = {
        "code": "CÓDIGO",
        "name": "NOMBRE",
        "abbreviation": "ABREVIACIÓN",
        "country_name": "PAÍS",
        "status_name": "ESTADO",
    }
    return handler.export_data(depts, DepartmentSerializer, field_mapping)


@api_view(["GET"])
@MiddlewareAutentication("general_master_department_template")
def department_template_view(request):
    headers = ["CÓDIGO", "NOMBRE", "ABREVIACIÓN", "PAÍS", "ESTADO"]
    handler = ExcelMasterHandler(Department, headers, "departamentos", request.user.id)
    return handler.generate_template()


@api_view(["POST"])
@MiddlewareAutentication("general_master_department_import")
@transaction.atomic
def department_import_view(request):
    headers = ["CÓDIGO", "NOMBRE", "ABREVIACIÓN", "PAÍS", "ESTADO"]
    handler = ExcelMasterHandler(Department, headers, "departamentos", request.user.id)
    field_mapping = {
        "CÓDIGO": "code",
        "NOMBRE": "name",
        "ABREVIACIÓN": "abbreviation",
    }

    def _audit_import(instance):
        save_audit_log(instance, request.user.id, EVENT_IMPORT)

    return handler.import_data(request, validate_department_import_row, field_mapping, audit_save_fn=_audit_import)
