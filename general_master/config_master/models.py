from django.db import models

from config.models import BaseModel

# Create your models here.


class Country(BaseModel):
    code = models.CharField(max_length=10)
    name = models.CharField(max_length=100)
    abbreviation = models.CharField(max_length=10)

    class Meta:
        db_table = "config_master_country"


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
