from django.contrib.gis.geos import Point
from django.test import TestCase
from service_directory.api.models import Country, CountryArea, Organisation, \
    Category, Service


class CountryTestCase(TestCase):
    def setUp(self):
        Country.objects.create(
            name='South Africa',
            iso_code='ZA'
        )

    def test_query(self):
        countries = Country.objects.filter(name='South Africa')

        self.assertEqual(1, len(countries))
        self.assertEqual('South Africa', countries[0].name)
        self.assertEqual('South Africa', countries[0].__unicode__())

    def test_update(self):
        countries = Country.objects.filter(name='South Africa')

        country = countries[0]
        country.iso_code = 'SA'
        country.save()

        countries = Country.objects.filter(name='South Africa')

        self.assertEqual(1, len(countries))
        self.assertEqual('SA', countries[0].iso_code)


class CountryAreaTestCase(TestCase):
    def setUp(self):
        self.country = Country.objects.create(
            name='South Africa',
            iso_code='ZA'
        )

        CountryArea.objects.create(
            name='Western Cape',
            level=CountryArea.AREA_LEVELS[0][0],  # Province/State
            country=self.country
        )

    def test_query(self):
        country_areas = CountryArea.objects.filter(name='Western Cape')

        self.assertEqual(1, len(country_areas))
        self.assertEqual('Western Cape', country_areas[0].name)
        self.assertEqual('Western Cape (Province/State in South Africa)',
                         country_areas[0].__unicode__())

    def test_update(self):
        country_areas = CountryArea.objects.filter(name='Western Cape')

        country_area = country_areas[0]
        country_area.name = 'WC'
        country_area.save()

        country_areas = CountryArea.objects.filter(name='WC')

        self.assertEqual(1, len(country_areas))
        self.assertEqual('WC', country_areas[0].name)


class OrganisationTestCase(TestCase):
    def setUp(self):
        self.country = Country.objects.create(
            name='South Africa',
            iso_code='ZA'
        )

        self.country_area_western_cape = CountryArea.objects.create(
            name='Western Cape',
            level=CountryArea.AREA_LEVELS[0][0],  # Province/State
            country=self.country
        )

        self.country_area_cape_town = CountryArea.objects.create(
            name='Cape Town',
            level=CountryArea.AREA_LEVELS[2][0],  # Municipality/City/Town
            country=self.country
        )

        org = Organisation.objects.create(
            name='Test Org',
            country=self.country,
        )

        org.areas.add(self.country_area_western_cape)
        org.areas.add(self.country_area_cape_town)

    def test_query(self):
        organisations = Organisation.objects.filter(name='Test Org')

        self.assertEqual(1, len(organisations))
        self.assertEqual('Test Org', organisations[0].name)
        self.assertEqual('Test Org', organisations[0].__unicode__())

    def test_update(self):
        organisations = Organisation.objects.filter(name='Test Org')

        organisation = organisations[0]
        organisation.name = 'Changed Org'
        organisation.save()

        organisations = Organisation.objects.filter(name='Changed Org')

        self.assertEqual(1, len(organisations))
        self.assertEqual('Changed Org', organisations[0].name)


class CategoryTestCase(TestCase):
    def setUp(self):
        Category.objects.create(name='Test Category')

    def test_query(self):
        categories = Category.objects.filter(name='Test Category')

        self.assertEqual(1, len(categories))
        self.assertEqual('Test Category', categories[0].name)
        self.assertEqual('Test Category', categories[0].__unicode__())

    def test_update(self):
        categories = Category.objects.filter(name='Test Category')

        category = categories[0]
        category.name = 'Changed Category'
        category.save()

        categories = Category.objects.filter(name='Changed Category')

        self.assertEqual(1, len(categories))
        self.assertEqual('Changed Category', categories[0].name)


class ServiceTestCase(TestCase):
    def setUp(self):
        self.country = Country.objects.create(
            name='South Africa',
            iso_code='ZA'
        )

        self.category = Category.objects.create(name='Test Category')

        self.organisation = Organisation.objects.create(
            name='Test Org',
            country=self.country,
            location=Point(-33.891937, 18.505496)
        )

        service = Service.objects.create(
            keywords='test',
            organisation=self.organisation
        )

        service.categories.add(self.category)

    def test_query(self):
        services = Service.objects.filter(organisation=self.organisation)

        self.assertEqual(1, len(services))
        self.assertEqual('test', services[0].keywords)
        self.assertEqual(
            'Categories: Test Category - Keywords: test - Organisation:'
            ' Test Org',
            services[0].__unicode__()
        )

    def test_update(self):
        services = Service.objects.filter(organisation=self.organisation)

        service = services[0]
        service.keywords = 'changed'
        service.save()

        services = Service.objects.filter(organisation=self.organisation)

        self.assertEqual(1, len(services))
        self.assertEqual('changed', services[0].keywords)
