from django.conf import settings
from django.contrib.gis.geos import Point
from django.test import TestCase
from haystack.backends.elasticsearch_backend import ElasticsearchSearchBackend
from rest_framework.test import APIClient
from service_directory.api.models import Country, Category, Organisation, \
    Service
from service_directory.api.search_indexes import ServiceIndex


class ServiceLookupTestCase(TestCase):
    client_class = APIClient

    @classmethod
    def setUpTestData(cls):
        # clear the haystack index which may have been left in a bad state by
        # other tests
        search_backend = ElasticsearchSearchBackend(
            'default',
            URL=settings.HAYSTACK_CONNECTIONS['default']['URL'],
            INDEX_NAME=settings.HAYSTACK_CONNECTIONS['default']['INDEX_NAME']
        )
        search_backend.clear()

        # this sets up the required mappings for us
        search_backend.update(ServiceIndex(), [])

        cls.country = Country.objects.create(
            name='South Africa',
            iso_code='ZA'
        )

        cls.category = Category.objects.create(name='Test Category')

        cls.org_cbmh = Organisation.objects.create(
            name='Netcare Christiaan Barnard Memorial Hospital',
            country=cls.country,
            location=Point(18.418231, -33.921859, srid=4326)
        )

        cls.org_khc = Organisation.objects.create(
            name='Kingsbury Hospital Claremont',
            country=cls.country,
            location=Point(18.469060, -33.986375, srid=4326)
        )

        cls.org_cmc = Organisation.objects.create(
            name='Constantiaberg Medi Clinic',
            country=cls.country,
            location=Point(18.461260, -34.026629, srid=4326)
        )

        test_service_1 = Service.objects.create(
            keywords='test heart transplant trauma',
            organisation=cls.org_cbmh
        )
        test_service_1.categories.add(cls.category)

        test_service_2 = Service.objects.create(
            keywords='test hiv aids',
            organisation=cls.org_khc
        )
        test_service_2.categories.add(cls.category)

        test_service_3 = Service.objects.create(
            keywords='test trauma accident',
            organisation=cls.org_cmc
        )
        test_service_3.categories.add(cls.category)

    def test_get_without_parameters(self):
        response = self.client.get('/api/service_lookup/', format='json')

        self.assertEqual(3, len(response.data))

    def test_get_with_keyword_parameter(self):
        response = self.client.get(
            '/api/service_lookup/',
            {'keyword': 'test'},
            format='json'
        )
        self.assertEqual(3, len(response.data))

        response = self.client.get(
            '/api/service_lookup/',
            {'keyword': 'heart'},
            format='json'
        )
        self.assertEqual(1, len(response.data))

        response = self.client.get(
            '/api/service_lookup/',
            {'keyword': 'hiv'},
            format='json'
        )
        self.assertEqual(1, len(response.data))

        response = self.client.get(
            '/api/service_lookup/',
            {'keyword': 'accident'},
            format='json'
        )
        self.assertEqual(1, len(response.data))

    def test_get_with_near_parameter(self):
        # -33.921387, 18.424101 - Adderley Street outside Cape Town station
        response = self.client.get(
            '/api/service_lookup/',
            {'near': '-33.921387,18.424101'},
            format='json'
        )

        # we should get all 3 services, ordered from closest to farthest
        # Christiaan Barnard Memorial Hospital is closest, followed by
        # Kingsbury Hospital Claremont and then Constantiaberg Medi Clinic
        self.assertEqual(3, len(response.data))

        self.assertEqual('test heart transplant trauma',
                         response.data[0]['keywords'])
        self.assertEqual('Netcare Christiaan Barnard Memorial Hospital',
                         response.data[0]['organisation']['name'])

        self.assertEqual('test hiv aids', response.data[1]['keywords'])
        self.assertEqual('Kingsbury Hospital Claremont',
                         response.data[1]['organisation']['name'])

        self.assertEqual('test trauma accident', response.data[2]['keywords'])
        self.assertEqual('Constantiaberg Medi Clinic',
                         response.data[2]['organisation']['name'])

    def test_get_with_keyword_and_near_parameters(self):
        # -33.921387, 18.424101 - Adderley Street outside Cape Town station
        response = self.client.get(
            '/api/service_lookup/',
            {
                'keyword': 'trauma',
                'near': '-33.921387,18.424101'
            },
            format='json'
        )

        # we should get 2 services, ordered from closest to farthest
        # Christiaan Barnard Memorial Hospital is closest
        self.assertEqual(2, len(response.data))

        self.assertEqual('test heart transplant trauma',
                         response.data[0]['keywords'])
        self.assertEqual('Netcare Christiaan Barnard Memorial Hospital',
                         response.data[0]['organisation']['name'])

        self.assertEqual('test trauma accident', response.data[1]['keywords'])
        self.assertEqual('Constantiaberg Medi Clinic',
                         response.data[1]['organisation']['name'])
