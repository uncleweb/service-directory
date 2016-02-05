from django.conf import settings
from django.contrib.gis.geos import Point
from django.test import TestCase
from haystack import signal_processor
from haystack.backends.elasticsearch_backend import ElasticsearchSearchBackend
from rest_framework.test import APIClient
from service_directory.api.models import Country, Category, Organisation, \
    Service, Keyword
from service_directory.api.search_indexes import ServiceIndex


def reset_haystack_index():
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


class ServiceLookupTestCase(TestCase):
    client_class = APIClient

    @classmethod
    def setUpTestData(cls):
        reset_haystack_index()

        cls.country = Country.objects.create(
            name='South Africa',
            iso_code='ZA'
        )

        cls.category = Category.objects.create(name='Test Category')

        cls.keyword_test = Keyword.objects.create(name='test')
        cls.keyword_test.categories.add(cls.category)

        cls.keyword_heart = Keyword.objects.create(name='heart')
        cls.keyword_heart.categories.add(cls.category)

        cls.keyword_transplant = Keyword.objects.create(name='transplant')
        cls.keyword_transplant.categories.add(cls.category)

        cls.keyword_trauma = Keyword.objects.create(name='trauma')
        cls.keyword_trauma.categories.add(cls.category)

        cls.keyword_hiv = Keyword.objects.create(name='hiv')
        cls.keyword_hiv.categories.add(cls.category)

        cls.keyword_aids = Keyword.objects.create(name='aids')
        cls.keyword_aids.categories.add(cls.category)

        cls.keyword_accident = Keyword.objects.create(name='accident')
        cls.keyword_accident.categories.add(cls.category)

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
            organisation=cls.org_cbmh
        )
        test_service_1.categories.add(cls.category)
        test_service_1.keywords.add(
            cls.keyword_test, cls.keyword_heart, cls.keyword_transplant,
            cls.keyword_trauma
        )

        test_service_2 = Service.objects.create(
            organisation=cls.org_khc
        )
        test_service_2.categories.add(cls.category)
        test_service_2.keywords.add(
            cls.keyword_test, cls.keyword_hiv, cls.keyword_aids
        )

        test_service_3 = Service.objects.create(
            organisation=cls.org_cmc
        )
        test_service_3.categories.add(cls.category)
        test_service_3.keywords.add(
            cls.keyword_test, cls.keyword_trauma, cls.keyword_accident
        )

        # Usually the middleware is responsible for doing this
        # See HaystackBatchFlushMiddleware & BatchingSignalProcessor
        #
        # We're using a custom SignalProcessor because calls to add() with M2M
        # relationships will not call save() methods and thus the haystack
        # RealtimeSignalProcessor will not know to update the index
        # see https://docs.djangoproject.com/en/1.8/ref/models/relations/
        # #django.db.models.fields.related.RelatedManager.add
        signal_processor.flush_changes()

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
            {'keyword': 'transplant'},
            format='json'
        )
        self.assertEqual(1, len(response.data))

        response = self.client.get(
            '/api/service_lookup/',
            {'keyword': 'trauma'},
            format='json'
        )
        self.assertEqual(2, len(response.data))

        response = self.client.get(
            '/api/service_lookup/',
            {'keyword': 'hiv'},
            format='json'
        )
        self.assertEqual(1, len(response.data))

        response = self.client.get(
            '/api/service_lookup/',
            {'keyword': 'aids'},
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

        self.assertListEqual(['test', 'heart', 'transplant', 'trauma'],
                             response.data[0]['keywords'])
        self.assertEqual('Netcare Christiaan Barnard Memorial Hospital',
                         response.data[0]['organisation']['name'])

        self.assertListEqual(['test', 'hiv', 'aids'],
                             response.data[1]['keywords'])
        self.assertEqual('Kingsbury Hospital Claremont',
                         response.data[1]['organisation']['name'])

        self.assertListEqual(['test', 'trauma', 'accident'],
                             response.data[2]['keywords'])
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

        self.assertListEqual(['test', 'heart', 'transplant', 'trauma'],
                             response.data[0]['keywords'])
        self.assertEqual('Netcare Christiaan Barnard Memorial Hospital',
                         response.data[0]['organisation']['name'])

        self.assertListEqual(['test', 'trauma', 'accident'],
                             response.data[1]['keywords'])
        self.assertEqual('Constantiaberg Medi Clinic',
                         response.data[1]['organisation']['name'])

    def test_fuzzy_matching(self):
        # match on keyword and category name
        response = self.client.get(
            '/api/service_lookup/',
            {
                'keyword': 'testt'
            },
            format='json'
        )

        self.assertEqual(3, len(response.data))

        # match on keyword name
        response = self.client.get(
            '/api/service_lookup/',
            {
                'keyword': 'aid'
            },
            format='json'
        )

        self.assertEqual(1, len(response.data))
        self.assertEqual('Kingsbury Hospital Claremont',
                         response.data[0]['organisation']['name'])

        # match on category name
        response = self.client.get(
            '/api/service_lookup/',
            {
                'keyword': 'category'
            },
            format='json'
        )

        self.assertEqual(3, len(response.data))

        # match on org name
        response = self.client.get(
            '/api/service_lookup/',
            {
                'keyword': 'med'
            },
            format='json'
        )

        self.assertEqual(1, len(response.data))
        self.assertEqual('Constantiaberg Medi Clinic',
                         response.data[0]['organisation']['name'])

        # match on org name
        response = self.client.get(
            '/api/service_lookup/',
            {
                'keyword': 'hospice'
            },
            format='json'
        )

        self.assertEqual(2, len(response.data))


class ServiceLookupWithoutDataTestCase(TestCase):
    client_class = APIClient

    @classmethod
    def setUpTestData(cls):
        reset_haystack_index()

    def test_get_without_parameters(self):
        # this is here purely to achieve 100% coverage
        # it tests the single statement that is otherwise missed in
        # ServiceLookup.get() - the last statement: return Response([])
        response = self.client.get('/api/service_lookup/', format='json')

        self.assertEqual(0, len(response.data))


class ServiceDetailTestCase(TestCase):
    client_class = APIClient

    @classmethod
    def setUpTestData(cls):
        cls.country = Country.objects.create(
            name='South Africa',
            iso_code='ZA'
        )

        cls.category = Category.objects.create(name='Test Category')

        cls.keyword = Keyword.objects.create(name='test')
        cls.keyword.categories.add(cls.category)

        cls.org = Organisation.objects.create(
            name='Test Organisation',
            country=cls.country,
            location=Point(18.505496, -33.891937, srid=4326)
        )

        cls.service = Service.objects.create(
            organisation=cls.org
        )
        cls.service.categories.add(cls.category)
        cls.service.keywords.add(cls.keyword)

    def test_get(self):
        response = self.client.get(
            '/api/service/{0}/'.format(self.service.id),
            format='json'
        )

        expected_response_content = '''
            {
                "id":%s,
                "verified_as":"",
                "age_range_min":null,
                "age_range_max":null,
                "availability_hours":"",
                "organisation":
                    {
                        "id":%s,
                        "name":"Test Organisation",
                        "about":"",
                        "address":"",
                        "telephone":"",
                        "email":"",
                        "web":"",
                        "location":"SRID=4326;\
POINT (18.5054960000000008 -33.8919369999999986)",
                        "country":%s
                    },
                "categories":[
                    {
                        "id":%s,
                        "name":"Test Category",
                        "show_on_home_page":false
                    }
                ],
                "keywords":[
                    {
                        "id":%s,
                        "name":"test",
                        "show_on_home_page":false,
                        "categories":[
                            %s
                        ]
                    }
                ]
            }
        ''' % (self.service.id, self.org.id, self.country.id, self.category.id,
               self.keyword.id, self.category.id)

        self.assertJSONEqual(response.content, expected_response_content)


class HomePageCategoryKeywordGroupingTestCase(TestCase):
    client_class = APIClient

    @classmethod
    def setUpTestData(cls):
        cls.category_1 = Category.objects.create(
            name='Test Category 1',
            show_on_home_page=True
        )
        cls.category_2 = Category.objects.create(
            name='Test Category 2',
            show_on_home_page=True
        )
        cls.category_3 = Category.objects.create(
            name='Test Category 3',
            show_on_home_page=True
        )
        cls.category_4 = Category.objects.create(
            name='Test Category 4',
            show_on_home_page=False
        )

        cls.keyword_1 = Keyword.objects.create(
            name='test1',
            show_on_home_page=True
        )
        cls.keyword_1.categories.add(cls.category_1)

        cls.keyword_2 = Keyword.objects.create(
            name='test2',
            show_on_home_page=False
        )
        cls.keyword_2.categories.add(cls.category_2)

        cls.keyword_3 = Keyword.objects.create(
            name='test3',
            show_on_home_page=True
        )
        cls.keyword_3.categories.add(cls.category_3, cls.category_4)

        cls.keyword_4 = Keyword.objects.create(
            name='test4',
            show_on_home_page=True
        )
        cls.keyword_4.categories.add(cls.category_4)

    def test_get(self):
        response = self.client.get(
            '/api/homepage_categories_keywords/',
            format='json'
        )

        # a category should only be returned if its show_on_home_page=True
        # a keyword should only be returned if its show_on_home_page=True
        # AND it belongs to at least one category whose show_on_home_page=True

        expected_response_content = '''
            [
                {
                    "name":"Test Category 1",
                    "keywords":[
                        "test1"
                    ]
                },
                {
                    "name":"Test Category 3",
                    "keywords":[
                        "test3"
                    ]
                }
            ]
        '''

        self.assertJSONEqual(response.content, expected_response_content)


class KeywordListTestCase(TestCase):
    client_class = APIClient

    @classmethod
    def setUpTestData(cls):
        cls.category_1 = Category.objects.create(
            name='Test Category 1'
        )
        cls.category_2 = Category.objects.create(
            name='Test Category 2'
        )

        cls.cat1kw1 = Keyword.objects.create(
            name='cat1kw1'
        )
        cls.cat1kw1.categories.add(cls.category_1)

        cls.cat1kw2 = Keyword.objects.create(
            name='cat1kw2'
        )
        cls.cat1kw2.categories.add(cls.category_1)

        cls.cat2kw1 = Keyword.objects.create(
            name='cat2kw1'
        )
        cls.cat2kw1.categories.add(cls.category_2)

        cls.cat2kw2 = Keyword.objects.create(
            name='cat2kw2'
        )
        cls.cat2kw2.categories.add(cls.category_2)

    def test_get_without_params(self):
        response = self.client.get(
            '/api/keywords/',
            format='json'
        )

        # all keywords should be returned
        self.assertEqual(4, len(response.data))

    def test_get_with_params(self):
        response = self.client.get(
            '/api/keywords/',
            {'category': self.category_1.name},
            format='json'
        )

        # cat1kw1 & cat1kw2 should be returned
        expected_response_content = '''
            [
                {
                    "id":%s,
                    "name":"%s",
                    "show_on_home_page":%s,
                    "categories":[
                        %s
                    ]
                },
                {
                    "id":%s,
                    "name":"%s",
                    "show_on_home_page":%s,
                    "categories":[
                        %s
                    ]
                }
            ]
        ''' % (self.cat1kw1.id, self.cat1kw1.name,
               str(self.cat1kw1.show_on_home_page).lower(), self.category_1.id,
               self.cat1kw2.id, self.cat1kw2.name,
               str(self.cat1kw2.show_on_home_page).lower(), self.category_1.id)

        self.assertJSONEqual(response.content, expected_response_content)

        response = self.client.get(
            '/api/keywords/',
            {'category': self.category_2.name},
            format='json'
        )

        # cat2kw1 & cat2kw2 should be returned
        expected_response_content = '''
            [
                {
                    "id":%s,
                    "name":"%s",
                    "show_on_home_page":%s,
                    "categories":[
                        %s
                    ]
                },
                {
                    "id":%s,
                    "name":"%s",
                    "show_on_home_page":%s,
                    "categories":[
                        %s
                    ]
                }
            ]
        ''' % (self.cat2kw1.id, self.cat2kw1.name,
               str(self.cat2kw1.show_on_home_page).lower(), self.category_2.id,
               self.cat2kw2.id, self.cat2kw2.name,
               str(self.cat2kw2.show_on_home_page).lower(), self.category_2.id)

        self.assertJSONEqual(response.content, expected_response_content)
