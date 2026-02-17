from rest_framework import serializers

from .models import Country


class CountrySerializer(serializers.ModelSerializer):
    status_name = serializers.CharField(source="status.name", read_only=True)

    class Meta:
        model = Country
        fields = [
            "id",
            "code",
            "name",
            "abbreviation",
            "status_name",
            "key_user_created",
            "key_user_updated",
            "created_at",
            "updated_at",
            "status",
        ]
        read_only_fields = ["key_user_created", "key_user_updated", "status"]
