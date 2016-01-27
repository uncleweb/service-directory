from __future__ import unicode_literals

from django.contrib.gis.db import models


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
        return '{0} ({1} in {2})'.format(
            self.name, self.get_level_display(), self.country
        )


class Organisation(models.Model):
    objects = models.GeoManager()

    name = models.CharField(max_length=100)
    about = models.CharField(max_length=500, blank=True)

    address = models.CharField(max_length=500, blank=True)
    telephone = models.CharField(max_length=50, blank=True)
    email = models.EmailField(blank=True)
    web = models.URLField(blank=True)

    country = models.ForeignKey(Country)
    areas = models.ManyToManyField(CountryArea)

    location = models.PointField(default='SRID=4326;POINT (0.0 0.0)', srid=4326)

    def __unicode__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(max_length=50)
    show_on_home_page = models.BooleanField(default=False)

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'categories'


class Keyword(models.Model):
    name = models.CharField(max_length=50)
    categories = models.ManyToManyField(Category)
    show_on_home_page = models.BooleanField(default=False)

    def __unicode__(self):
        return self.name

    def formatted_categories(self):
        categories = [
            category.__unicode__() for category in self.categories.all()
        ]
        return ', '.join(categories)
    formatted_categories.short_description = 'Categories'


class Service(models.Model):
    objects = models.GeoManager()

    categories = models.ManyToManyField(Category)
    keywords = models.ManyToManyField(Keyword)

    organisation = models.ForeignKey(Organisation)

    verified_as = models.CharField(max_length=100, blank=True)

    age_range_min = models.PositiveSmallIntegerField(blank=True, null=True)
    age_range_max = models.PositiveSmallIntegerField(blank=True, null=True)

    # might want separate min & max fields / DateTimeField or DurationField
    availability_hours = models.CharField(max_length=50, blank=True)

    def formatted_categories(self):
        categories = [
            category.__unicode__() for category in self.categories.all()
        ]
        return ', '.join(categories)
    formatted_categories.short_description = 'Categories'

    def formatted_keywords(self):
        keywords = [
            keyword.__unicode__() for keyword in self.keywords.all()
        ]
        return ', '.join(keywords)
    formatted_keywords.short_description = 'Keywords'
