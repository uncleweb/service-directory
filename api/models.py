from __future__ import unicode_literals

from django.db import models


class Country(models.Model):
    name = models.CharField(max_length=100)
    iso_code = models.CharField(max_length=3)

    def __unicode__(self):
        return self.name

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

    def __unicode__(self):
        return '{0} ({1} in {2})'.format(self.name, self.get_level_display(), self.country)


class Organisation(models.Model):
    name = models.CharField(max_length=100)
    about = models.CharField(max_length=500, blank=True)

    address = models.CharField(max_length=500, blank=True)
    telephone = models.CharField(max_length=50, blank=True)
    email = models.EmailField(blank=True)
    web = models.URLField(blank=True)

    country = models.ForeignKey(Country)
    areas = models.ManyToManyField(CountryArea)

    # TODO: lat/lon, consider GeoDjango

    def __unicode__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(max_length=50)

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'categories'


class Service(models.Model):
    categories = models.ManyToManyField(Category)
    keywords = models.CharField(max_length=500)

    organisation = models.ForeignKey(Organisation)

    verified_as = models.CharField(max_length=100, blank=True)

    age_range_min = models.PositiveSmallIntegerField(blank=True, null=True)
    age_range_max = models.PositiveSmallIntegerField(blank=True, null=True)

    availability_hours = models.CharField(max_length=50, blank=True)  # might want separate min & max fields / DateTimeField or DurationField

    def __unicode__(self):
        category_names = [cat.__unicode__() for cat in self.categories.all()]
        return 'Categories: {0} - Keywords: {1} - Organisation: {2}'.format(','.join(category_names), self.keywords, self.organisation)
