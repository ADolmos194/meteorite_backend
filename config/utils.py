from functools import wraps

from rest_framework import status
from rest_framework.response import Response

from access.models import Permission, PermissionRole, UserRole

# ---------------------------------------------------------
# CONSTANTES DE ESTADO (UUIDs)
# ---------------------------------------------------------
STATUS_BORRADOR = "ab8a2bef-e236-4d73-99b1-f8c988be2e99"
STATUS_EN_REVISION = "09618606-d931-428a-aee4-e45032c00310"
STATUS_APROBADO = "6d025ac4-3d4f-4889-b9d2-64afc723c299"
STATUS_RECHAZADO = "c370c327-f93d-4cc6-b566-8945da77ee0d"
STATUS_BLOQUEADO = "45eca1ed-2f98-4b92-b677-492d190cae86"
STATUS_SUSPENDIDO = "91adf4bd-e05d-4230-9fd9-6510d6889516"
STATUS_EXPIRADO = "29f770db-5d6b-49c9-8b58-87ede5b395fd"
STATUS_ERROR = "a12400ea-0643-4ea1-ab7d-b9b54d55b0e8"
STATUS_ENVIADO = "b4d35209-2fa2-422c-bf81-d647599310a5"
STATUS_RECIBIDO = "8e5124d7-b0f1-4db0-820e-625f66b9b3b2"
STATUS_FALLIDO = "c2807e6c-1730-46cc-8ede-3cb5bdf623e8"
STATUS_SINCRONIZADO = "995a6208-2818-423c-badb-727237c967df"
STATUS_ARCHIVADO = "e217fae9-6cf8-4a32-b2d2-d5de1adf6c00"
STATUS_ACTIVO = "2bd04756-cf71-438d-b8be-7d6dd58e5e34"
STATUS_INACTIVO = "742ab54f-c5ab-4a41-93e3-373e1d9c4105"
STATUS_ANULADO = "bd7a3ed1-efdb-429b-9cb2-9999b7a12bab"
STATUS_ELIMINADO = "87ed0a4c-df78-4c53-8fd8-0463d634ec98"
STATUS_PENDIENTE = "ff2b0252-5a55-4789-90e6-a18ac3f6e569"
STATUS_PROCESADO = "48d43356-2fd9-494f-989d-113bbfbc6f90"
STATUS_COMPLETADO = "139b8dd1-f244-4295-9996-692a66a9c455"

# Mapeo opcional para búsquedas inversas o iteraciones
STATUS_MAP = {
    STATUS_BORRADOR: "BORRADOR",
    STATUS_EN_REVISION: "EN REVISIÓN",
    STATUS_APROBADO: "APROBADO",
    STATUS_RECHAZADO: "RECHAZADO",
    STATUS_BLOQUEADO: "BLOQUEADO",
    STATUS_SUSPENDIDO: "SUSPENDIDO",
    STATUS_EXPIRADO: "EXPIRADO",
    STATUS_ERROR: "ERROR",
    STATUS_ENVIADO: "ENVIADO",
    STATUS_RECIBIDO: "RECIBIDO",
    STATUS_FALLIDO: "FALLIDO",
    STATUS_SINCRONIZADO: "SINCRONIZADO",
    STATUS_ARCHIVADO: "ARCHIVADO",
    STATUS_ACTIVO: "ACTIVO",
    STATUS_INACTIVO: "INACTIVO",
    STATUS_ANULADO: "ANULADO",
    STATUS_ELIMINADO: "ELIMINADO",
    STATUS_PENDIENTE: "PENDIENTE",
    STATUS_PROCESADO: "PROCESADO",
    STATUS_COMPLETADO: "COMPLETADO",
}


# ---------------------------------------------------------
# FUNCIONES DE RESPUESTA PERSONALIZADAS
# ---------------------------------------------------------
def succescall(data=None, message="Operación exitosa"):
    return Response(
        {"status": "success", "message": message, "data": data},
        status=status.HTTP_200_OK,
    )


def succesresponse(data=None, message="Operación exitosa"):
    return succescall(data, message)


def warningcall(message="Advertencia de negocio"):
    return Response(
        {"status": "warning", "message": message, "data": None},
        status=status.HTTP_400_BAD_REQUEST,
    )


def warningresponse(message="Advertencia de negocio"):
    return warningcall(message)


def errorcall(
    message="Error crítico", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
):
    return Response(
        {"status": "error", "message": message, "data": None}, status=status_code
    )


def errorresponse(
    message="Error crítico", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
):
    return errorcall(message, status_code)


# ---------------------------------------------------------
# MIDDLEWARE DE AUTENTICACIÓN PERSONALIZADO
# ---------------------------------------------------------
def MiddlewareAutentication(decorator_name):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return errorcall("No autenticado", status.HTTP_401_UNAUTHORIZED)

            # 1. Obtener Roles del usuario
            user_roles = UserRole.objects.filter(
                user_id=request.user.id
            ).select_related("role")
            roles = [ur.role for ur in user_roles]
            role_names = [r.name for r in roles]

            # 2. Verificar si es Superusuario o tiene "ALL PERMISSIONS"
            if "ALL PERMISSIONS" in role_names or getattr(
                request.user, "is_admin", False
            ):
                return view_func(request, *args, **kwargs)

            # 3. Verificar permiso específico por decorator_name
            has_permission = PermissionRole.objects.filter(
                role__in=roles, permission__decorator_name=decorator_name
            ).exists()

            if has_permission:
                return view_func(request, *args, **kwargs)

            return errorcall(
                f"No tiene permisos para realizar esta acción ({decorator_name})",
                status.HTTP_403_FORBIDDEN,
            )

        return _wrapped_view

    return decorator
