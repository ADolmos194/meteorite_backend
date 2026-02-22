from django.db import models
from django.db.models import Q
from config.models import BaseModel
from config.utils import STATUS_ANULADO

# Create your models here.


class Country(BaseModel):
    code = models.CharField(max_length=10)
    name = models.CharField(max_length=100)
    abbreviation = models.CharField(max_length=10)
    iso_alpha_2 = models.CharField(max_length=2, null=True, blank=True)
    iso_alpha_3 = models.CharField(max_length=3, null=True, blank=True)
    phone_prefix = models.CharField(max_length=10, null=True, blank=True)

    class Meta:
        db_table = "config_master_country"
        constraints = [
            models.UniqueConstraint(
                fields=["code"],
                condition=~Q(status_id=STATUS_ANULADO),
                name="unique_country_code_not_annulled"
            ),
            models.UniqueConstraint(
                fields=["name"],
                condition=~Q(status_id=STATUS_ANULADO),
                name="unique_country_name_not_annulled"
            ),
            models.UniqueConstraint(
                fields=["iso_alpha_2"],
                condition=~Q(status_id=STATUS_ANULADO),
                name="unique_iso_alpha_2_not_annulled"
            ),
            models.UniqueConstraint(
                fields=["iso_alpha_3"],
                condition=~Q(status_id=STATUS_ANULADO),
                name="unique_iso_alpha_3_not_annulled"
            )
        ]


class Money(BaseModel):
    code = models.CharField(max_length=10)
    name = models.CharField(max_length=100)
    symbol = models.CharField(max_length=10)
    key_country = models.ForeignKey(Country, on_delete=models.CASCADE)

    class Meta:
        db_table = "config_master_money"


class Department(BaseModel):
    code = models.CharField(max_length=10)
    name = models.CharField(max_length=100)
    abbreviation = models.CharField(max_length=10)
    key_country = models.ForeignKey(Country, on_delete=models.CASCADE)

    class Meta:
        db_table = "config_master_department"
        constraints = [
            models.UniqueConstraint(
                fields=["code", "key_country"],
                condition=~Q(status_id=STATUS_ANULADO),
                name="unique_department_code_per_country_not_annulled"
            ),
            models.UniqueConstraint(
                fields=["name", "key_country"],
                condition=~Q(status_id=STATUS_ANULADO),
                name="unique_department_name_per_country_not_annulled"
            )
        ]


class Province(BaseModel):
    code = models.CharField(max_length=10)
    name = models.CharField(max_length=100)
    abbreviation = models.CharField(max_length=10)
    key_department = models.ForeignKey(Department, on_delete=models.CASCADE)

    class Meta:
        db_table = "config_master_province"


class District(BaseModel):
    code = models.CharField(max_length=10)
    name = models.CharField(max_length=100)
    abbreviation = models.CharField(max_length=10)
    key_province = models.ForeignKey(Province, on_delete=models.CASCADE)

    class Meta:
        db_table = "config_master_district"


class Society(BaseModel):
    code = models.CharField(max_length=10)
    name = models.CharField(max_length=100)
    abbreviation = models.CharField(max_length=10)
    key_country = models.ForeignKey(Country, on_delete=models.CASCADE)
    key_department = models.ForeignKey(Department, on_delete=models.CASCADE)
    key_province = models.ForeignKey(Province, on_delete=models.CASCADE)
    key_district = models.ForeignKey(District, on_delete=models.CASCADE)

    class Meta:
        db_table = "config_master_society"
