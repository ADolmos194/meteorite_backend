from rest_framework import serializers

from .models import Status


class StatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Status
        fields = [
            "id",
            "name",
            "description",
            "color_code",
            "icon",
            "type_status"]
