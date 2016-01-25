from models import Country, CountryArea, Organisation, Category, Service, \
    Keyword
from django.contrib.gis import admin
from service_directory.api.forms import OrganisationModelForm


class CountryAreaModelAdmin(admin.ModelAdmin):
    list_display = ('name', 'level', 'country')


class OrganisationModelAdmin(admin.OSMGeoAdmin):
    form = OrganisationModelForm
    list_display = ('name', 'country')


class KeywordModelAdmin(admin.ModelAdmin):
    list_display = ('name', 'formatted_categories')


class ServiceModelAdmin(admin.ModelAdmin):
    list_display = ('organisation', 'formatted_categories',
                    'formatted_keywords')


# Register your models here.
admin.site.register(Country)
admin.site.register(CountryArea, CountryAreaModelAdmin)
admin.site.register(Organisation, OrganisationModelAdmin)
admin.site.register(Category)
admin.site.register(Keyword, KeywordModelAdmin)
admin.site.register(Service, ServiceModelAdmin)
