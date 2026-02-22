from rest_framework import serializers
from .models import Country, Department


class CountrySerializer(serializers.ModelSerializer):
    status_name = serializers.CharField(source="status.name", read_only=True)

    class Meta:
        model = Country
        fields = [
            "id",
            "code",
            "name",
            "abbreviation",
            "iso_alpha_2",
            "iso_alpha_3",
            "phone_prefix",
            "status_name",
            "key_user_created",
            "key_user_updated",
            "created_at",
            "updated_at",
            "status",
        ]
        read_only_fields = ["key_user_created", "key_user_updated", "status"]


class DepartmentSerializer(serializers.ModelSerializer):
    status_name = serializers.CharField(source="status.name", read_only=True)
    country_name = serializers.CharField(source="key_country.name", read_only=True)

    class Meta:
        model = Department
        fields = [
            "id",
            "code",
            "name",
            "abbreviation",
            "key_country",
            "country_name",
            "status_name",
            "key_user_created",
            "key_user_updated",
            "created_at",
            "updated_at",
            "status",
        ]
        read_only_fields = ["key_user_created", "key_user_updated", "status"]
