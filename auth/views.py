import os
import secrets

from django.contrib.auth import authenticate, login, logout
from django.db import transaction
from django.middleware.csrf import get_token
from django.utils import timezone
from django.views.decorators.csrf import ensure_csrf_cookie
from rest_framework import status
from rest_framework.decorators import api_view, throttle_classes
from rest_framework.throttling import AnonRateThrottle

from access.models import Menu, PermissionRole, RoleMenu, UserRole
from config.utils import errorcall, succescall

from .models import User, VerificationCode
from .serializers import (
    LoginSerializer,
    ResendCodeSerializer,
    UserRegisterSerializer,
    VerifyCodeSerializer,
)
from .utils import (
    MSG_ACCOUNT_CREATED,
    MSG_CODE_VERIFIED,
    MSG_ENTER_CODE,
    MSG_INVALID_CODE,
    MSG_INVALID_CREDENTIALS,
    MSG_INVALID_SYSTEM,
    MSG_LOGIN_SUCCESS,
    MSG_USER_BLOCKED,
    MSG_USER_INACTIVE,
)


class LoginRateThrottle(AnonRateThrottle):
    """
    Throttle estricto para el endpoint de login:
    máx 10 intentos/minuto por IP.
    """
    scope = "login"


def build_menu_tree(menus, parent=None):
    """
    Recursive function to build a hierarchical menu.
    """
    tree = []
    # Filter menus by parent
    level_menus = [m for m in menus if m.parent == parent]

    # Sort by ordering
    level_menus.sort(key=lambda x: x.ordering)

    for menu in level_menus:
        node = {
            "id": str(menu.id),
            "subject": menu.subject,
            "description": menu.description,
            "title": menu.title,
            "icon": menu.icon,
            "ordering": menu.ordering,
            "to": menu.to or "root",
            "children": build_menu_tree(menus, parent=menu),
        }
        tree.append(node)

    return tree


def get_user_session_data(user):
    """
    Helper function to gather user info, menus, and permissions.
    """
    # 1. Obtener Roles del usuario
    user_roles = UserRole.objects.filter(
        user_id=user.id).select_related("role")
    roles = [ur.role for ur in user_roles]
    role_names = [r.name for r in roles]

    # 2. Verificar si es Superusuario o tiene "ALL PERMISSIONS"
    is_all_permissions = "ALL PERMISSIONS" in role_names or user.is_admin

    # 3. Obtener Menús permitidos
    if is_all_permissions:
        allowed_menus = list(Menu.objects.all())
    else:
        role_menu_ids = RoleMenu.objects.filter(role__in=roles).values_list(
            "menu_id", flat=True
        )
        allowed_menus = list(
            Menu.objects.filter(
                id__in=role_menu_ids).distinct())

    # 4. Obtener Permisos
    if is_all_permissions:
        permisos_back = ["ALL_PERMISSIONS"]
        permisos_front = [{"action": "manage", "subject": "all"}]
    else:
        perms = PermissionRole.objects.filter(role__in=roles).select_related(
            "permission"
        )
        permisos_back = list(set([p.permission.name for p in perms]))
        permisos_front = [{"action": "read", "subject": p}
                          for p in permisos_back]

    return {
        "user_info": {
            "id": str(user.id),
            "username": user.username,
            "name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
            "dni": user.dni or "",
            "role": is_all_permissions,
            "menu": build_menu_tree(allowed_menus),
            "permisos_front": permisos_front,
            "permisos_back": permisos_back,
        }
    }


@api_view(["GET"])
@ensure_csrf_cookie
def session_view(request):
    """
    Returns user info if the session is valid.
    """
    if not request.user.is_authenticated:
        return errorcall("No autenticado", status.HTTP_401_UNAUTHORIZED)

    data = get_user_session_data(request.user)
    data["csrfToken"] = get_token(request)
    return succescall(data, "Sesión válida")


@api_view(["POST"])
@ensure_csrf_cookie
@transaction.atomic
def register_view(request):
    # Política de limpieza: Eliminar usuarios inactivos previos con el mismo
    # email o username
    email = request.data.get("email")
    username = request.data.get("username")
    if email:
        User.objects.filter(email=email, is_active=False).delete()
    if username:
        User.objects.filter(username=username, is_active=False).delete()

    serializer = UserRegisterSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()

        # Generar código de verificación de 6 dígitos de forma segura
        code = "".join([secrets.choice("0123456789") for _ in range(6)])
        VerificationCode.objects.create(user=user, code=code)

        # Simulación de envío de email (loguear en consola)
        print(f"DEBUG: Enviando código {code} al email {user.email}")

        # Envío real de email
        from django.core.mail import send_mail
        try:
            send_mail(
                subject="Verifica tu cuenta - Yachay Agro",
                message=(
                    f"Tu código de verificación para Yachay Agro es: {code}"
                ),
                from_email=None,  # Usa DEFAULT_FROM_EMAIL de settings
                recipient_list=[user.email],
                fail_silently=True,
            )
        except Exception as e:
            print(f"ERROR enviando email: {e}")

        return succescall(
            {
                "instruction": MSG_ENTER_CODE,
                # Solo exponer el código en modo DEBUG (nunca en producción)
                **({
                    "debug_code": code
                } if os.getenv("DEBUG", "True") == "True" else {}),
            },
            MSG_ACCOUNT_CREATED,
        )
    return errorcall(serializer.errors, status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
@ensure_csrf_cookie
def verify_code_view(request):
    serializer = VerifyCodeSerializer(data=request.data)
    if serializer.is_valid():
        email = serializer.validated_data["email"]
        code_str = serializer.validated_data["code"]

        try:
            user = User.objects.get(email=email)
            verification = VerificationCode.objects.filter(
                user=user, code=code_str, is_used=False
            ).latest("created_at")

            if verification.is_expired():
                user.delete()
                return errorcall(
                    "Código expirado. Tu cuenta ha sido eliminada por "
                    "seguridad, por favor regístrate de nuevo.",
                    status.HTTP_400_BAD_REQUEST,
                )

            # Activar usuario
            user.is_active = True
            user.save()

            # Marcar código como usado
            verification.is_used = True
            verification.save()

            return succescall(None, MSG_CODE_VERIFIED)

        except (User.DoesNotExist, VerificationCode.DoesNotExist):
            return errorcall(MSG_INVALID_CODE, status.HTTP_400_BAD_REQUEST)

    return errorcall(serializer.errors, status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
@ensure_csrf_cookie
@throttle_classes([LoginRateThrottle])
def login_view(request):
    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid():
        username = serializer.validated_data["username"]
        password = serializer.validated_data["password"]
        system_id = serializer.validated_data["system"]

        # Validar ID de sistema
        if system_id != os.getenv("SYSTEM_ID"):
            return errorcall(MSG_INVALID_SYSTEM, status.HTTP_403_FORBIDDEN)

        user = User.objects.filter(username=username).first()

        if not user:
            return errorcall(
                MSG_INVALID_CREDENTIALS,
                status.HTTP_401_UNAUTHORIZED)

        # Verificar si está bloqueado por demasiados intentos (ejemplo: 5)
        if user.failed_login_attempts >= 5:
            return errorcall(MSG_USER_BLOCKED, status.HTTP_403_FORBIDDEN)

        authenticated_user = authenticate(username=username, password=password)

        if authenticated_user:
            if not authenticated_user.is_active:
                # Verificar si el último código ya expiró antes de intentar
                # auto-reenviar
                last_verification = (
                    VerificationCode.objects.filter(
                        user=authenticated_user,
                        is_used=False) .order_by("-created_at") .first())

                if last_verification and last_verification.is_expired():
                    authenticated_user.delete()
                    return errorcall(
                        "Cuenta eliminada por falta de verificación "
                        "oportuna. Regístrate de nuevo.",
                        status.HTTP_403_FORBIDDEN,
                    )

                # Si no ha expirado o es la primera vez, auto-reenviar (o
                # simplemente reenviar el mismo)
                # Generar y enviar un nuevo código automáticamente al intentar
                # login
                code = "".join([secrets.choice("0123456789")
                               for _ in range(6)])
                VerificationCode.objects.create(
                    user=authenticated_user, code=code)

                # Loguear en consola
                print(
                    f"DEBUG: Auto-reenviando código {code} al email "
                    f"{authenticated_user.email} tras intento de login"
                )

                # Envío real de email
                from django.core.mail import send_mail
                try:
                    send_mail(
                        subject="Verifica tu cuenta - Yachay Agro",
                        message=(
                            "Has intentado iniciar sesión. Tu nuevo código "
                            f"de verificación es: {code}"
                        ),
                        from_email=None,
                        recipient_list=[
                            authenticated_user.email],
                        fail_silently=True,
                    )
                except Exception as e:
                    print(f"ERROR auto-reenviando email: {e}")

                return errorcall(
                    MSG_USER_INACTIVE,
                    status.HTTP_403_FORBIDDEN,
                    data={
                        "instruction": MSG_ENTER_CODE,
                        "email": authenticated_user.email,
                        **({
                            "debug_code": code
                        } if os.getenv("DEBUG", "True") == "True" else {}),
                    },
                )

            # Éxito: crear sesión de Django
            login(request, authenticated_user)

            # Resetear intentos fallidos
            authenticated_user.failed_login_attempts = 0
            authenticated_user.save()

            # Recopilar datos de sesión
            data = get_user_session_data(authenticated_user)
            data["csrfToken"] = get_token(request)

            return succescall(data, MSG_LOGIN_SUCCESS)
        else:
            # Fallo: incrementar intentos
            user.failed_login_attempts += 1
            user.last_failed_login = timezone.now()
            user.save()

            if user.failed_login_attempts >= 5:
                return errorcall(MSG_USER_BLOCKED, status.HTTP_403_FORBIDDEN)

            return errorcall(
                MSG_INVALID_CREDENTIALS,
                status.HTTP_401_UNAUTHORIZED)

    return errorcall(serializer.errors, status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
def logout_view(request):
    logout(request)  # flush() de la sesión en BD + regenera session key
    response = succescall(None, "Cierre de sesión exitoso")
    # Eliminar las cookies del cliente: al reingresar se genera una sesión
    # nueva
    response.delete_cookie("sessionid")
    response.delete_cookie("csrftoken")
    return response


@api_view(["POST"])
@ensure_csrf_cookie
@transaction.atomic
def resend_code_view(request):
    serializer = ResendCodeSerializer(data=request.data)
    if serializer.is_valid():
        email = serializer.validated_data["email"]
        user = User.objects.filter(email=email, is_active=False).first()

        if not user:
            # Por seguridad, si el usuario no existe o ya está activo, no damos
            # pistas extras
            return succescall(
                None, "Si el correo es válido, recibirás un nuevo código.")

        # Generar nuevo código
        code = "".join([secrets.choice("0123456789") for _ in range(6)])
        VerificationCode.objects.create(user=user, code=code)

        # Loguear en consola
        print(f"DEBUG: Reenviando código {code} al email {user.email}")

        # Envío real de email
        from django.core.mail import send_mail

        try:
            send_mail(
                subject="Tu nuevo código - Yachay Agro",
                message=f"Tu nuevo código de verificación es: {code}",
                from_email=None,
                recipient_list=[user.email],
                fail_silently=True,
            )
        except Exception as e:
            print(f"ERROR reenviando email: {e}")

        response_data = {}
        if os.getenv("DEBUG", "True") == "True":
            response_data["debug_code"] = code

        return succescall(response_data, "Nuevo código enviado con éxito")

    return errorcall(serializer.errors, status.HTTP_400_BAD_REQUEST)
