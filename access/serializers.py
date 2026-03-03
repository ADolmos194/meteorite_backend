from rest_framework import serializers

from .models import (
    Action,
    Event,
    Group,
    Menu,
    Permission,
    PermissionRole,
    PermissionSystem,
    Role,
    RoleMenu,
    System,
    UserGroup,
    UserGroupRole,
    UserRole,
)


class SystemSerializer(serializers.ModelSerializer):
    status_name = serializers.CharField(
        source="status.name", read_only=True)

    class Meta:
        model = System
        fields = [
            "id", "name", "description",
            "status_name", "status",
            "key_user_created", "key_user_updated",
            "created_at", "updated_at",
        ]
        read_only_fields = ["key_user_created", "key_user_updated", "status"]


class MenuSerializer(serializers.ModelSerializer):
    status_name = serializers.CharField(
        source="status.name", read_only=True)
    parent_title = serializers.CharField(
        source="parent.title", read_only=True, default=None)

    class Meta:
        model = Menu
        fields = [
            "id", "subject", "description", "title", "icon",
            "ordering", "to", "parent", "parent_title",
            "status_name", "status",
            "key_user_created", "key_user_updated",
            "created_at", "updated_at",
        ]
        read_only_fields = ["key_user_created", "key_user_updated", "status"]


class ActionSerializer(serializers.ModelSerializer):
    status_name = serializers.CharField(
        source="status.name", read_only=True)

    class Meta:
        model = Action
        fields = [
            "id", "name", "description",
            "status_name", "status",
            "key_user_created", "key_user_updated",
            "created_at", "updated_at",
        ]
        read_only_fields = ["key_user_created", "key_user_updated", "status"]


class EventSerializer(serializers.ModelSerializer):
    status_name = serializers.CharField(
        source="status.name", read_only=True)

    class Meta:
        model = Event
        fields = [
            "id", "name", "description",
            "status_name", "status",
            "key_user_created", "key_user_updated",
            "created_at", "updated_at",
        ]
        read_only_fields = ["key_user_created", "key_user_updated", "status"]


class RoleSerializer(serializers.ModelSerializer):
    status_name = serializers.CharField(
        source="status.name", read_only=True)

    class Meta:
        model = Role
        fields = [
            "id", "name", "description",
            "status_name", "status",
            "key_user_created", "key_user_updated",
            "created_at", "updated_at",
        ]
        read_only_fields = ["key_user_created", "key_user_updated", "status"]


class GroupSerializer(serializers.ModelSerializer):
    status_name = serializers.CharField(
        source="status.name", read_only=True)

    class Meta:
        model = Group
        fields = [
            "id", "name", "description",
            "status_name", "status",
            "key_user_created", "key_user_updated",
            "created_at", "updated_at",
        ]
        read_only_fields = ["key_user_created", "key_user_updated", "status"]


class PermissionSerializer(serializers.ModelSerializer):
    status_name = serializers.CharField(
        source="status.name", read_only=True)

    class Meta:
        model = Permission
        fields = [
            "id", "name", "decorator_name", "api_url", "description",
            "status_name", "status",
            "key_user_created", "key_user_updated",
            "created_at", "updated_at",
        ]
        read_only_fields = ["key_user_created", "key_user_updated", "status"]


# ─── Pivote: UserRole ────────────────────────────────────────────────────────
class UserRoleSerializer(serializers.ModelSerializer):
    role_name = serializers.CharField(source="role.name", read_only=True)
    status_name = serializers.CharField(
        source="status.name", read_only=True)

    class Meta:
        model = UserRole
        fields = [
            "id", "user_id", "role", "role_name",
            "status_name", "status",
            "key_user_created", "key_user_updated",
            "created_at", "updated_at",
        ]
        read_only_fields = ["key_user_created", "key_user_updated", "status"]


# ─── Pivote: UserGroup ───────────────────────────────────────────────────────
class UserGroupSerializer(serializers.ModelSerializer):
    group_name = serializers.CharField(source="group.name", read_only=True)
    status_name = serializers.CharField(
        source="status.name", read_only=True)

    class Meta:
        model = UserGroup
        fields = [
            "id", "user_id", "group", "group_name",
            "status_name", "status",
            "key_user_created", "key_user_updated",
            "created_at", "updated_at",
        ]
        read_only_fields = ["key_user_created", "key_user_updated", "status"]


# ─── Pivote: UserGroupRole ───────────────────────────────────────────────────
class UserGroupRoleSerializer(serializers.ModelSerializer):
    group_name = serializers.CharField(source="group.name", read_only=True)
    role_name = serializers.CharField(source="role.name", read_only=True)
    status_name = serializers.CharField(
        source="status.name", read_only=True)

    class Meta:
        model = UserGroupRole
        fields = [
            "id", "user_id", "group", "group_name", "role", "role_name",
            "status_name", "status",
            "key_user_created", "key_user_updated",
            "created_at", "updated_at",
        ]
        read_only_fields = ["key_user_created", "key_user_updated", "status"]


# ─── Pivote: PermissionRole ──────────────────────────────────────────────────
class PermissionRoleSerializer(serializers.ModelSerializer):
    permission_name = serializers.CharField(
        source="permission.name", read_only=True)
    permission_decorator = serializers.CharField(
        source="permission.decorator_name", read_only=True)
    role_name = serializers.CharField(source="role.name", read_only=True)
    status_name = serializers.CharField(
        source="status.name", read_only=True)

    class Meta:
        model = PermissionRole
        fields = [
            "id", "permission", "permission_name", "permission_decorator",
            "role", "role_name",
            "status_name", "status",
            "key_user_created", "key_user_updated",
            "created_at", "updated_at",
        ]
        read_only_fields = ["key_user_created", "key_user_updated", "status"]


# ─── Pivote: PermissionSystem ────────────────────────────────────────────────
class PermissionSystemSerializer(serializers.ModelSerializer):
    permission_name = serializers.CharField(
        source="permission.name", read_only=True)
    system_name = serializers.CharField(
        source="system.name", read_only=True)
    status_name = serializers.CharField(
        source="status.name", read_only=True)

    class Meta:
        model = PermissionSystem
        fields = [
            "id", "permission", "permission_name",
            "system", "system_name",
            "status_name", "status",
            "key_user_created", "key_user_updated",
            "created_at", "updated_at",
        ]
        read_only_fields = ["key_user_created", "key_user_updated", "status"]


# ─── Pivote: RoleMenu ────────────────────────────────────────────────────────
class RoleMenuSerializer(serializers.ModelSerializer):
    role_name = serializers.CharField(source="role.name", read_only=True)
    menu_title = serializers.CharField(source="menu.title", read_only=True)
    status_name = serializers.CharField(
        source="status.name", read_only=True)

    class Meta:
        model = RoleMenu
        fields = [
            "id", "role", "role_name", "menu", "menu_title",
            "status_name", "status",
            "key_user_created", "key_user_updated",
            "created_at", "updated_at",
        ]
        read_only_fields = ["key_user_created", "key_user_updated", "status"]
