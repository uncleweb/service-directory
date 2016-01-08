from __future__ import unicode_literals

from django.db import models


class Country(models.Model):
    name = models.CharField(max_length=100)
    iso_code = models.CharField(max_length=3)

    class Meta:
        verbose_name_plural = 'countries'


class CountryArea(models.Model):
    AREA_LEVELS = [
        (1, 'Province/State'),
        (2, 'Region'),
        (3, 'Municipality/City/Town'),
        (4, 'Suburb/Area')
    ]

    name = models.CharField(max_length=100)
    level = models.IntegerField(choices=AREA_LEVELS)
    country = models.ForeignKey(Country)


class Organisation(models.Model):
    name = models.CharField(max_length=100)
    about = models.CharField(max_length=500)

    address = models.CharField(max_length=500)
    telephone = models.CharField(max_length=50)
    email = models.EmailField()
    web = models.URLField()

    country = models.ForeignKey(Country)
    areas = models.ManyToManyField(CountryArea)

    # TODO: lat/lon, consider GeoDjango


class Category(models.Model):
    name = models.CharField(max_length=50)

    class Meta:
        verbose_name_plural = 'categories'


class Service(models.Model):
    categories = models.ManyToManyField(Category)
    keywords = models.CharField(max_length=500)

    organisation = models.ForeignKey(Organisation)

    verified_as = models.CharField(max_length=100)

    age_range_min = models.PositiveSmallIntegerField()
    age_range_max = models.PositiveSmallIntegerField()

    availability_hours = models.CharField(max_length=50)  # might want separate min & max fields / DateTimeField or DurationField
