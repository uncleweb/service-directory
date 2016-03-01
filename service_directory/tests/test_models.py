from datetime import datetime, timedelta

from django.contrib.gis.geos import Point
from django.test import TestCase
from pytz import utc
from service_directory.api.models import Country, Organisation, \
    Category, Service, Keyword, ServiceIncorrectInformationReport, \
    ServiceRating


class CountryTestCase(TestCase):
    def setUp(self):
        country = Country.objects.create(
            name='South Africa',
            iso_code='ZA'
        )
        country.full_clean()  # force model validation to happen

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
        self.country.full_clean()  # force model validation to happen

        org = Organisation.objects.create(
            name='Test Org',
            country=self.country,
            location=Point(18.505496, -33.891937, srid=4326)
        )
        org.full_clean()  # force model validation to happen

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
        cat = Category.objects.create(name='Test Category')
        cat.full_clean()  # force model validation to happen

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
        self.category.full_clean()  # force model validation to happen

        keyword = Keyword.objects.create(name='test')
        keyword.full_clean()  # force model validation to happen
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
        self.country.full_clean()  # force model validation to happen

        self.category = Category.objects.create(name='Test Category')
        self.category.full_clean()  # force model validation to happen

        self.keyword = Keyword.objects.create(name='test')
        self.keyword.full_clean()  # force model validation to happen
        self.keyword.categories.add(self.category)

        self.organisation = Organisation.objects.create(
            name='Test Org',
            country=self.country,
            location=Point(18.505496, -33.891937, srid=4326)
        )
        self.organisation.full_clean()  # force model validation to happen

        service = Service.objects.create(
            name='Test Service',
            organisation=self.organisation
        )
        service.full_clean()  # force model validation to happen
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


class ServiceIncorrectInformationReportTestCase(TestCase):
    def setUp(self):
        self.country = Country.objects.create(
            name='South Africa',
            iso_code='ZA'
        )
        self.country.full_clean()  # force model validation to happen

        self.category = Category.objects.create(name='Test Category')
        self.category.full_clean()  # force model validation to happen

        self.keyword = Keyword.objects.create(name='test')
        self.keyword.full_clean()  # force model validation to happen
        self.keyword.categories.add(self.category)

        self.organisation = Organisation.objects.create(
            name='Test Org',
            country=self.country,
            location=Point(18.505496, -33.891937, srid=4326)
        )
        self.organisation.full_clean()  # force model validation to happen

        self.service = Service.objects.create(
            name='Test Service',
            organisation=self.organisation
        )
        self.service.full_clean()  # force model validation to happen
        self.service.categories.add(self.category)
        self.service.keywords.add(self.keyword)

        report = ServiceIncorrectInformationReport.objects.create(
            service=self.service,
            contact_details=True
        )
        report.full_clean()  # force model validation to happen

    def test_query(self):
        reports = ServiceIncorrectInformationReport.objects.filter(
            service=self.service
        )

        self.assertEqual(1, len(reports))
        self.assertTrue(reports[0].contact_details)
        self.assertIsNone(reports[0].address)
        self.assertIsNone(reports[0].trading_hours)
        self.assertIsNone(reports[0].other)
        self.assertEqual('', reports[0].other_detail)

        self.assertAlmostEqual(
            datetime.now(utc),
            reports[0].reported_at,
            delta=timedelta(seconds=10)
        )

    def test_update(self):
        report = ServiceIncorrectInformationReport.objects.filter(
            service=self.service
        ).get()

        report.other = True
        report.other_detail = 'Test'
        report.save()

        report.refresh_from_db()
        self.assertTrue(report.other)
        self.assertEqual('Test', report.other_detail)


class ServiceRatingTestCase(TestCase):
    def setUp(self):
        self.country = Country.objects.create(
            name='South Africa',
            iso_code='ZA'
        )
        self.country.full_clean()  # force model validation to happen

        self.category = Category.objects.create(name='Test Category')
        self.category.full_clean()  # force model validation to happen

        self.keyword = Keyword.objects.create(name='test')
        self.keyword.full_clean()  # force model validation to happen
        self.keyword.categories.add(self.category)

        self.organisation = Organisation.objects.create(
            name='Test Org',
            country=self.country,
            location=Point(18.505496, -33.891937, srid=4326)
        )
        self.organisation.full_clean()  # force model validation to happen

        self.service = Service.objects.create(
            name='Test Service',
            organisation=self.organisation
        )
        self.service.full_clean()  # force model validation to happen
        self.service.categories.add(self.category)
        self.service.keywords.add(self.keyword)

        rating = ServiceRating.objects.create(
            service=self.service,
            rating=ServiceRating.AVERAGE
        )
        rating.full_clean()  # force model validation to happen

    def test_query(self):
        ratings = ServiceRating.objects.filter(
            service=self.service
        )

        self.assertEqual(1, len(ratings))
        self.assertEqual(ServiceRating.AVERAGE, ratings[0].rating)

        self.assertAlmostEqual(
            datetime.now(utc),
            ratings[0].rated_at,
            delta=timedelta(seconds=10)
        )

    def test_update(self):
        rating = ServiceRating.objects.filter(
            service=self.service
        ).get()

        rating.rating = ServiceRating.GOOD
        rating.save()

        rating.refresh_from_db()
        self.assertEqual(ServiceRating.GOOD, rating.rating)
