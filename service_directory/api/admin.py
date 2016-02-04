from django.contrib.gis.geos import Point
from django.core.exceptions import ValidationError
from django.utils.encoding import force_text
from import_export.widgets import ManyToManyWidget, ForeignKeyWidget, Widget
from models import Country, Organisation, Category, Service, \
    Keyword
from django.contrib.gis import admin
from service_directory.api.forms import OrganisationModelForm

from import_export import resources
from import_export.admin import ImportExportMixin
from import_export import fields as import_field


class PointWidget(Widget):
    def clean(self, value):
        try:
            lat, lng = value.split(',')
            lat = float(lat)
            lng = float(lng)
            point = Point(lng, lat, srid=4326)
        except ValueError:
            raise ValidationError(
                'Invalid coordinates. Coordinates must be comma-separated'
                ' latitude,longitude decimals, eg: "-33.921124,18.417313"'
            )

        return point

    def render(self, value):
        return force_text('{0},{1}'.format(value.y, value.x))


class CategoryResource(resources.ModelResource):
    class Meta:
        model = Category
        import_id_fields = ('name',)
        fields = ('name', 'show_on_home_page',)


class KeywordResource(resources.ModelResource):
    def import_obj(self, obj, data, dry_run):
        keyword_category_names_set = set(
            data.get('categories', u'').split(',')
        )

        db_categories = Category.objects.filter(
            name__in=keyword_category_names_set
        )

        db_categories_set = set(
            [db_category.name for db_category in db_categories]
        )

        if keyword_category_names_set != db_categories_set:
            missing_categories = keyword_category_names_set.difference(
                db_categories_set
            )
            raise ValidationError(
                u"Keyword '{0}' is being imported with "
                u"Categories that are missing and "
                u"need to be imported/created: {1}".format(
                    data.get('name', u''), missing_categories)
            )

        return super(KeywordResource, self).import_obj(obj, data, dry_run)

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


class OrganisationResource(resources.ModelResource):
    def import_obj(self, obj, data, dry_run):
        organisation_country_names_set = set(
            data.get('country', u'').split(',')
        )

        db_countries = Country.objects.filter(
            name__in=organisation_country_names_set
        )

        db_countries_set = set(
            [db_country.name for db_country in db_countries]
        )

        if organisation_country_names_set != db_countries_set:
            missing_countries = organisation_country_names_set.difference(
                db_countries_set
            )
            raise ValidationError(
                u"Organisation '{0}' is being imported with "
                u"Countries that are missing and "
                u"need to be imported/created: {1}".format(
                    data.get('name', u''), missing_countries)
            )

        return super(OrganisationResource, self).import_obj(obj, data, dry_run)

    country = import_field.Field(
        attribute='country',
        column_name='country',
        widget=ForeignKeyWidget(
            Country,
            field='name'
        ))

    location = import_field.Field(
        attribute='location',
        column_name='location',
        widget=PointWidget()
    )

    class Meta:
        model = Organisation


class ServiceResource(resources.ModelResource):
    def import_obj(self, obj, data, dry_run):
        # check categories
        service_category_names_set = set(
            data.get('categories', u'').split(',')
        )

        db_categories = Category.objects.filter(
            name__in=service_category_names_set
        )

        db_categories_set = set(
            [db_category.name for db_category in db_categories]
        )

        if service_category_names_set != db_categories_set:
            missing_categories = service_category_names_set.difference(
                db_categories_set
            )
            raise ValidationError(
                u"Service '{0}' is being imported with "
                u"Categories that are missing and "
                u"need to be imported/created: {1}".format(
                    data.get('id', u''), missing_categories)
            )

        # check keywords
        service_keyword_names_set = set(
            data.get('keywords', u'').split(',')
        )

        db_keywords = Keyword.objects.filter(
            name__in=service_keyword_names_set
        )

        db_keywords_set = set(
            [db_keyword.name for db_keyword in db_keywords]
        )

        if service_keyword_names_set != db_keywords_set:
            missing_keywords = service_keyword_names_set.difference(
                db_keywords_set
            )
            raise ValidationError(
                u"Service '{0}' is being imported with "
                u"Keywords that are missing and "
                u"need to be imported/created: {1}".format(
                    data.get('id', u''), missing_keywords)
            )

        return super(ServiceResource, self).import_obj(obj, data, dry_run)

    categories = import_field.Field(
        attribute='categories',
        column_name='categories',
        widget=ManyToManyWidget(
            Category,
            field='name'
        ))

    keywords = import_field.Field(
        attribute='keywords',
        column_name='keywords',
        widget=ManyToManyWidget(
            Keyword,
            field='name'
        ))

    class Meta:
        model = Service


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


# Register your models here.
admin.site.register(Country, CountryModelAdmin)
admin.site.register(Organisation, OrganisationModelAdmin)
admin.site.register(Category, CategoryModelAdmin)
admin.site.register(Keyword, KeywordModelAdmin)
admin.site.register(Service, ServiceModelAdmin)
