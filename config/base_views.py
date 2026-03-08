import copy
from django.db import transaction
from rest_framework import status
from rest_framework.decorators import api_view
from drf_spectacular.utils import extend_schema, OpenApiTypes
from django.db.models import Q

from .utils import (
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
    save_audit_log,
)

class BaseViewFactory:
    """
    Factory to generate standard CRUD views with automatic auditing.
    """
    def __init__(self, model, serializer_class, module_name, permission_prefix):
        self.model = model
        self.serializer_class = serializer_class
        self.module_name = module_name
        self.permission_prefix = permission_prefix

    def get_view(self, filters=None, order_by=None):
        """
        filters: list of strings representing fields to filter from request.data
        """
        @extend_schema(request=None, responses={200: self.serializer_class(many=True)})
        @MiddlewareAutentication(f"{self.permission_prefix}_get")
        @api_view(["POST"])
        def view(request):
            status_filter = request.data.get("status", None)
            page = int(request.data.get("page", 1))
            page_size = min(int(request.data.get("page_size", 10)), 200)

            qs = self.model.objects.exclude(status_id=STATUS_ANULADO)
            if status_filter == "activo":
                qs = qs.filter(status_id=STATUS_ACTIVO)
            elif status_filter == "inactivo":
                qs = qs.filter(status_id=STATUS_INACTIVO)
            
            # Filtros personalizados (ej: user_id, group_id)
            if filters:
                for f in filters:
                    val = request.data.get(f)
                    if val:
                        qs = qs.filter(**{f: val})

            # Búsqueda genérica
            query = request.data.get("query", "").strip()
            if query and hasattr(self.model, 'name'):
                qs = qs.filter(name__icontains=query)
            elif query and hasattr(self.model, 'title'):
                qs = qs.filter(title__icontains=query)

            if order_by:
                qs = qs.order_by(*order_by) if isinstance(order_by, list) else qs.order_by(order_by)
            else:
                qs = qs.order_by("-created_at") if hasattr(self.model, 'created_at') else qs.order_by("id")
            
            total = qs.count()
            start = (page - 1) * page_size
            end = start + page_size
            serializer = self.serializer_class(qs[start:end], many=True)
            return succescall({
                "results": serializer.data,
                "total": total,
                "page": page,
                "page_size": page_size,
                "pages": (total + page_size - 1) // page_size,
            }, f"Lista de {self.module_name} obtenida")
        return view

    def select_view(self, order_by=None):
        @extend_schema(request=None, responses={200: self.serializer_class(many=True)})
        @MiddlewareAutentication(f"{self.permission_prefix}_select")
        @api_view(["POST"])
        def view(request):
            qs = self.model.objects.filter(status_id=STATUS_ACTIVO)
            if order_by:
                qs = qs.order_by(*order_by) if isinstance(order_by, list) else qs.order_by(order_by)
            elif hasattr(self.model, 'name'):
                qs = qs.order_by("name")
            elif hasattr(self.model, 'title'):
                qs = qs.order_by("title")
            serializer = self.serializer_class(qs, many=True)
            return succescall(serializer.data, f"{self.module_name} activos obtenidos")
        return view

    def create_view(self, unique_fields=None):
        @extend_schema(request=self.serializer_class, responses={201: self.serializer_class})
        @MiddlewareAutentication(f"{self.permission_prefix}_create")
        @api_view(["POST"])
        def view(request):
            if unique_fields:
                q_obj = Q()
                for field in unique_fields:
                    val = request.data.get(field)
                    if val is not None:
                        q_obj &= Q(**{f"{field}": val}) # Simplificado para UUIDs/IDs
                
                if q_obj and self.model.objects.filter(q_obj).exclude(status_id=STATUS_ANULADO).exists():
                    return errorcall("Este registro ya existe", status.HTTP_400_BAD_REQUEST)

            serializer = self.serializer_class(data=request.data)
            if serializer.is_valid():
                instance = serializer.save(
                    key_user_created_id=request.user.id,
                    key_user_updated_id=request.user.id,
                    status_id=STATUS_ACTIVO,
                )
                save_audit_log(instance, request.user.id, EVENT_CREATE)
                return succescall(serializer.data, f"{self.module_name} creado")
            return errorcall(serializer.errors, status.HTTP_400_BAD_REQUEST)
        return view

    def update_view(self, unique_fields=None):
        @extend_schema(request=self.serializer_class, responses={200: self.serializer_class})
        @MiddlewareAutentication(f"{self.permission_prefix}_update")
        @api_view(["PATCH"])
        def view(request):
            pk = request.data.get("id")
            instance = self.model.objects.filter(pk=pk).first()
            if not instance:
                return errorcall(f"{self.module_name} no encontrado", status.HTTP_404_NOT_FOUND)

            if unique_fields:
                q_obj = Q()
                for field in unique_fields:
                    val = request.data.get(field)
                    if val is not None:
                        q_obj &= Q(**{f"{field}": val})
                
                if q_obj and self.model.objects.filter(q_obj).exclude(pk=pk).exclude(status_id=STATUS_ANULADO).exists():
                    return errorcall("Ya existe otro registro con estos datos", status.HTTP_400_BAD_REQUEST)

            serializer = self.serializer_class(instance, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save(key_user_updated_id=request.user.id)
                save_audit_log(instance, request.user.id, EVENT_UPDATE)
                return succescall(serializer.data, f"{self.module_name} actualizado")
            return errorcall(serializer.errors, status.HTTP_400_BAD_REQUEST)
        return view

    def bulk_assign_view(self, target_field, item_field, extra_fields=None):
        """
        Asignación masiva: ej. asignar varios roles a un usuario.
        target_field: 'user_id'
        item_field: 'role_id'
        extra_fields: ['group_id'] (otros campos necesarios para la relación)
        request.data: { 'user_id': '...', 'role_ids': ['...', '...'], 'group_id': '...' }
        """
        @extend_schema(request=None, responses={200: OpenApiTypes.STR})
        @MiddlewareAutentication(f"{self.permission_prefix}_assign")
        @api_view(["POST"])
        def view(request):
            target_id = request.data.get(target_field)
            
            # Detectar IDs (puede venir como 'role_id' o 'role_ids')
            single_id = request.data.get(item_field) or request.data.get(f"{item_field}_id")
            multiple_ids = request.data.get(f"{item_field}s") or request.data.get(f"{item_field}_ids") or []
            
            item_ids = multiple_ids if isinstance(multiple_ids, list) else []
            if single_id and single_id not in item_ids:
                item_ids.append(single_id)
            
            # Recopilar data extra
            extra_data = {}
            if extra_fields:
                for ef in extra_fields:
                    val = request.data.get(ef)
                    if val: extra_data[ef] = val

            if not target_id or not item_ids:
                return errorcall("Datos incompletos", status.HTTP_400_BAD_REQUEST)
            
            count = 0
            with transaction.atomic():
                for i_id in item_ids:
                    # Filtro base para duplicados
                    filter_kwargs = {
                        target_field: target_id,
                        item_field: i_id,
                        **extra_data
                    }
                    
                    exists = self.model.objects.filter(**filter_kwargs).exclude(status_id=STATUS_ANULADO).exists()
                    
                    if not exists:
                        instance = self.model.objects.create(**{
                            **filter_kwargs,
                            "key_user_created_id": request.user.id,
                            "key_user_updated_id": request.user.id,
                            "status_id": STATUS_ACTIVO
                        })
                        save_audit_log(instance, request.user.id, EVENT_CREATE)
                        count += 1
            
            return succescall(None, f"{count} asignaciones creadas")
        return view

    def status_change_view(self, target_status, event_type):
        @extend_schema(request=None, responses={200: OpenApiTypes.STR})
        @MiddlewareAutentication(f"{self.permission_prefix}_{target_status.lower() if target_status != STATUS_ANULADO else 'annul'}")
        @api_view(["PATCH", "DELETE"]) # Permitir DELETE para compatibilidad con removals
        def view(request):
            pks = request.data.get("ids", [])
            pk = request.data.get("id")
            if pk: pks.append(pk)
            
            if not pks:
                return errorcall("IDs no proporcionados", status.HTTP_400_BAD_REQUEST)
            
            items = self.model.objects.filter(pk__in=pks)
            count = items.count()
            
            with transaction.atomic():
                for item in items:
                    if target_status == "DELETE":
                        save_audit_log(item, request.user.id, EVENT_ANNUL) # Log antes de borrar
                        item.delete()
                    else:
                        item.status_id = target_status
                        item.key_user_updated_id = request.user.id
                        item.save()
                        save_audit_log(item, request.user.id, event_type)
            
            return succescall(None, f"{count} registros procesados")
        return view
