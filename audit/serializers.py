from rest_framework import serializers
from .models import AuditLog, AuditLogDetail
from auth.models import User

class AuditLogDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuditLogDetail
        fields = '__all__'

class AuditLogSerializer(serializers.ModelSerializer):
    user_name = serializers.SerializerMethodField()
    
    class Meta:
        model = AuditLog
        fields = '__all__'

    def get_user_name(self, obj):
        try:
            user = User.objects.get(id=obj.key_user)
            return user.username
        except User.DoesNotExist:
            return "Usuario no encontrado"
