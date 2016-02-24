from django.contrib.gis import admin
from import_export.admin import ImportExportMixin
from models import Country, Organisation, Category, Service, Keyword, \
    ServiceIncorrectInformationReport
from service_directory.api.admin_import_export import CountryResource, \
    OrganisationResource, CategoryResource, KeywordResource, ServiceResource
from service_directory.api.admin_model_forms import OrganisationModelForm


class CountryModelAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display = ('name', 'iso_code')
    resource_class = CountryResource


class OrganisationModelAdmin(ImportExportMixin, admin.OSMGeoAdmin):
    form = OrganisationModelForm
    list_display = ('name', 'country')
    resource_class = OrganisationResource

    def get_form(self, request, obj=None, **kwargs):
        form = super(OrganisationModelAdmin, self).get_form(
            request, obj, **kwargs
        )

        # populate the location_coords field when editing
        if obj:
            form.declared_fields['location_coords'].initial = \
                '{0}, {1}'.format(obj.location.y, obj.location.x)

        return form


class CategoryModelAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display = ('name', 'show_on_home_page')
    resource_class = CategoryResource


class KeywordModelAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display = ('name', 'formatted_categories', 'show_on_home_page')
    resource_class = KeywordResource


class ServiceModelAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display = ('organisation', 'formatted_categories',
                    'formatted_keywords')
    resource_class = ServiceResource


class ServiceIncorrectInformationReportModelAdmin(admin.ModelAdmin):
    """
    We disallow adding, modifying or deleting ServiceIncorrectInformationReport
    instances as these should only be created through the API and not modified
    afterwards.
    Currently this is the easiest way to have a 'read-only' model in admin.
    """
    actions = None

    readonly_fields = ('service', 'reported_at', 'contact_details',
                       'address', 'trading_hours', 'other', 'other_detail')

    list_display = ('service', 'reported_at')

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


# Register your models here.
admin.site.register(Country, CountryModelAdmin)
admin.site.register(Organisation, OrganisationModelAdmin)
admin.site.register(Category, CategoryModelAdmin)
admin.site.register(Keyword, KeywordModelAdmin)
admin.site.register(Service, ServiceModelAdmin)
admin.site.register(
    ServiceIncorrectInformationReport,
    ServiceIncorrectInformationReportModelAdmin
)
