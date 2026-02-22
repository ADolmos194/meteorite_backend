from django.db import models

from config.models import BaseModel


class System(BaseModel):
    name = models.CharField(max_length=50)
    description = models.TextField()

    def __str__(self):
        return self.name

    class Meta:
        db_table = "acc_system"


class Menu(BaseModel):
    subject = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    title = models.CharField(max_length=100)
    icon = models.CharField(max_length=100, null=True, blank=True)
    ordering = models.IntegerField(default=0)
    to = models.CharField(max_length=255, null=True, blank=True)
    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="children")

    def __str__(self):
        return self.title

    class Meta:
        db_table = "acc_menu"


class Action(BaseModel):
    name = models.CharField(max_length=50)
    description = models.TextField()

    def __str__(self):
        return self.name

    class Meta:
        db_table = "acc_action"


class Event(BaseModel):
    name = models.CharField(max_length=50)
    description = models.TextField()

    def __str__(self):
        return self.name

    class Meta:
        db_table = "acc_event"


class Role(BaseModel):
    name = models.CharField(max_length=50)
    description = models.TextField()

    def __str__(self):
        return self.name

    class Meta:
        db_table = "acc_role"


class UserRole(BaseModel):
    user_id = models.UUIDField(db_index=True)
    role = models.ForeignKey(Role, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.user_id)

    class Meta:
        db_table = "acc_user_role"


class Group(BaseModel):
    name = models.CharField(max_length=50)
    description = models.TextField()

    def __str__(self):
        return self.name

    class Meta:
        db_table = "acc_group"


class UserGroup(BaseModel):
    user_id = models.UUIDField(db_index=True)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.user_id)

    class Meta:
        db_table = "acc_user_group"


class UserGroupRole(BaseModel):
    user_id = models.UUIDField(db_index=True)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    role = models.ForeignKey(Role, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.user_id)

    class Meta:
        db_table = "acc_user_group_role"


class Permission(BaseModel):
    name = models.CharField(max_length=50)
    decorator_name = models.TextField()
    api_url = models.TextField()
    description = models.TextField()

    class Meta:
        db_table = "acc_permission"


class PermissionRole(BaseModel):
    permission = models.ForeignKey(Permission, on_delete=models.CASCADE)
    role = models.ForeignKey(Role, on_delete=models.CASCADE)

    def __str__(self):
        return self.permission.name

    class Meta:
        db_table = "acc_permission_role"


class PermissionSystem(BaseModel):
    permission = models.ForeignKey(Permission, on_delete=models.CASCADE)
    system = models.ForeignKey(System, on_delete=models.CASCADE)

    def __str__(self):
        return self.permission.name

    class Meta:
        db_table = "acc_permission_system"


class RoleMenu(BaseModel):
    role = models.ForeignKey(
        Role,
        on_delete=models.CASCADE,
        related_name="role_menus")
    menu = models.ForeignKey(
        Menu,
        on_delete=models.CASCADE,
        related_name="role_menus")

    def __str__(self):
        return f"{self.role.name} - {self.menu.title}"

    class Meta:
        db_table = "acc_role_menu"
        unique_together = ("role", "menu")
