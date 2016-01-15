from models import Country, CountryArea, Organisation, Category, Service
from django.contrib.gis import admin
from service_directory.api.forms import OrganisationModelForm


class OrganisationModelAdmin(admin.OSMGeoAdmin):
    form = OrganisationModelForm


# Register your models here.
admin.site.register(Country)
admin.site.register(CountryArea)
admin.site.register(Organisation, OrganisationModelAdmin)
admin.site.register(Category)
admin.site.register(Service)
