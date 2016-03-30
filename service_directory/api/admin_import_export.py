from django.contrib.gis.geos import Point
from django.core.exceptions import ValidationError
from django.utils.encoding import force_text
from import_export import fields as import_export_fields
from import_export import resources
from import_export.widgets import ManyToManyWidget, ForeignKeyWidget, Widget
from service_directory.api.models import Category, Keyword, Country, \
    Organisation, OrganisationIncorrectInformationReport, OrganisationRating


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


class CountryResource(resources.ModelResource):
    class Meta:
        model = Country
        import_id_fields = ('name',)
        fields = ('name', 'iso_code',)


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

    categories = import_export_fields.Field(
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


class OrganisationResource(resources.ModelResource):
    def import_obj(self, obj, data, dry_run):
        # check countries
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

        return super(OrganisationResource, self).import_obj(obj, data, dry_run)

    country = import_export_fields.Field(
        attribute='country',
        column_name='country',
        widget=ForeignKeyWidget(
            Country,
            field='name'
        ))

    location = import_export_fields.Field(
        attribute='location',
        column_name='location',
        widget=PointWidget()
    )

    categories = import_export_fields.Field(
        attribute='categories',
        column_name='categories',
        widget=ManyToManyWidget(
            Category,
            field='name'
        ))

    keywords = import_export_fields.Field(
        attribute='keywords',
        column_name='keywords',
        widget=ManyToManyWidget(
            Keyword,
            field='name'
        ))

    class Meta:
        model = Organisation


class OrganisationIncorrectInformationReportResource(resources.ModelResource):
    organisation = import_export_fields.Field(
        attribute='organisation__name', column_name='organisation'
    )

    class Meta:
        model = OrganisationIncorrectInformationReport

        fields = ('organisation', 'contact_details', 'address',
                  'trading_hours', 'other', 'other_detail', 'reported_at')

        export_order = ('organisation', 'contact_details', 'address',
                        'trading_hours', 'other', 'other_detail',
                        'reported_at')


class OrganisationRatingResource(resources.ModelResource):
    organisation = import_export_fields.Field(
        attribute='organisation__name', column_name='organisation'
    )

    class Meta:
        model = OrganisationRating
        fields = ('organisation', 'rating', 'rated_at')
        export_order = ('organisation', 'rating', 'rated_at')
