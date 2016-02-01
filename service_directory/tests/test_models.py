from django.contrib.gis.geos import Point
from django.test import TestCase
from service_directory.api.models import Country, Organisation, \
    Category, Service, Keyword


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


class OrganisationTestCase(TestCase):
    def setUp(self):
        self.country = Country.objects.create(
            name='South Africa',
            iso_code='ZA'
        )

        Organisation.objects.create(
            name='Test Org',
            country=self.country,
            location=Point(18.505496, -33.891937, srid=4326)
        )

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


class KeywordTestCase(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name='Test Category')

        keyword = Keyword.objects.create(name='test')

        keyword.categories.add(self.category)

    def test_query(self):
        keywords = Keyword.objects.filter(name='test')

        self.assertEqual(1, len(keywords))
        self.assertTrue('Test Category' in keywords[0].formatted_categories())
        self.assertEqual('test', keywords[0].__unicode__())

    def test_update(self):
        keyword = Keyword.objects.filter(name='test').get()

        keyword.name = 'test changed'
        keyword.save()

        keyword.refresh_from_db()
        self.assertEqual('test changed', keyword.name)


class ServiceTestCase(TestCase):
    def setUp(self):
        self.country = Country.objects.create(
            name='South Africa',
            iso_code='ZA'
        )

        self.category = Category.objects.create(name='Test Category')

        self.keyword = Keyword.objects.create(name='test')
        self.keyword.categories.add(self.category)

        self.organisation = Organisation.objects.create(
            name='Test Org',
            country=self.country,
            location=Point(18.505496, -33.891937, srid=4326)
        )

        service = Service.objects.create(
            organisation=self.organisation
        )

        service.categories.add(self.category)
        service.keywords.add(self.keyword)

    def test_query(self):
        services = Service.objects.filter(organisation=self.organisation)

        self.assertEqual(1, len(services))
        self.assertTrue('Test Category' in services[0].formatted_categories())
        self.assertTrue('test' in services[0].formatted_keywords())

    def test_update(self):
        service = Service.objects.filter(organisation=self.organisation).get()

        service.verified_as = 'Child Friendly'
        service.save()

        service.refresh_from_db()
        self.assertEqual('Child Friendly', service.verified_as)
