from import_export.widgets import ManyToManyWidget, ForeignKeyWidget
from models import Country, CountryArea, Organisation, Category, Service, \
    Keyword
from django.contrib.gis import admin
from service_directory.api.forms import OrganisationModelForm

from import_export import resources
from import_export.admin import ImportExportMixin
from import_export import fields as import_field


class CategoryResource(resources.ModelResource):
    class Meta:
        model = Category
        import_id_fields = ('name',)
        fields = ('name', 'show_on_home_page',)


class KeywordResource(resources.ModelResource):
    categories = import_field.Field(
            attribute='categories',
            column_name='categories',
            widget=ManyToManyWidget(
                Category,
                field='name'
            ))

    class Meta:
        model = Keyword
        import_id_fields = ('name',)
        fields = ('name', 'categories', 'show_on_home_page',)


class CountryResource(resources.ModelResource):
    class Meta:
        model = Country
        import_id_fields = ('name',)
        fields = ('name', 'iso_code',)


class CountryAreaResource(resources.ModelResource):
    country = import_field.Field(
            attribute='country',
            column_name='country',
            widget=ForeignKeyWidget(
                Country,
                field='name'
            ))

    class Meta:
        model = CountryArea
        import_id_fields = ('name', 'level',)
        fields = ('name', 'level', 'country',)


class CountryModelAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display = ('name', 'iso_code')
    resource_class = CountryResource


class CountryAreaModelAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display = ('name', 'level', 'country')
    resource_class = CountryAreaResource


class OrganisationModelAdmin(admin.OSMGeoAdmin):
    form = OrganisationModelForm
    list_display = ('name', 'country')


class CategoryModelAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display = ('name', 'show_on_home_page')
    resource_class = CategoryResource


class KeywordModelAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display = ('name', 'formatted_categories', 'show_on_home_page')
    resource_class = KeywordResource


class ServiceModelAdmin(admin.ModelAdmin):
    list_display = ('organisation', 'formatted_categories',
                    'formatted_keywords')


# Register your models here.
admin.site.register(Country, CountryModelAdmin)
admin.site.register(CountryArea, CountryAreaModelAdmin)
admin.site.register(Organisation, OrganisationModelAdmin)
admin.site.register(Category, CategoryModelAdmin)
admin.site.register(Keyword, KeywordModelAdmin)
admin.site.register(Service, ServiceModelAdmin)
