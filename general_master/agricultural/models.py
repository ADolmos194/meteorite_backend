from django.db import models

from config.models import BaseModel
from general_master.config_master.models import (
    Country,
    Department,
    District,
    Province,
    Society,
)


# Create your models here.
class Crop(BaseModel):
    name = models.CharField(max_length=100)
    abbreviation = models.CharField(max_length=10)
    key_country = models.ForeignKey(Country, on_delete=models.CASCADE)
    key_department = models.ForeignKey(Department, on_delete=models.CASCADE)
    key_province = models.ForeignKey(Province, on_delete=models.CASCADE)
    key_district = models.ForeignKey(District, on_delete=models.CASCADE)
    key_society = models.ForeignKey(Society, on_delete=models.CASCADE)

    class Meta:
        db_table = "agc_crop"


class Farm(BaseModel):
    name = models.CharField(max_length=100)
    abbreviation = models.CharField(max_length=10)
    key_country = models.ForeignKey(Country, on_delete=models.CASCADE)
    key_department = models.ForeignKey(Department, on_delete=models.CASCADE)
    key_province = models.ForeignKey(Province, on_delete=models.CASCADE)
    key_district = models.ForeignKey(District, on_delete=models.CASCADE)
    key_society = models.ForeignKey(Society, on_delete=models.CASCADE)

    class Meta:
        db_table = "agc_farm"


class Field(BaseModel):
    name = models.CharField(max_length=100)
    abbreviation = models.CharField(max_length=10)
    key_farm = models.ForeignKey(Farm, on_delete=models.CASCADE)

    class Meta:
        db_table = "agc_field"


class Stage(BaseModel):
    name = models.CharField(max_length=100)
    abbreviation = models.CharField(max_length=10)
    key_field = models.ForeignKey(Field, on_delete=models.CASCADE)

    class Meta:
        db_table = "agc_stage"


class Shift(BaseModel):
    name = models.CharField(max_length=100)
    abbreviation = models.CharField(max_length=10)
    key_stage = models.ForeignKey(Stage, on_delete=models.CASCADE)

    class Meta:
        db_table = "agc_shift"
