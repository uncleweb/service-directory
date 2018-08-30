from datetime import datetime, timedelta

import re
from dateutil.parser import parse

from django.conf import settings
from django.contrib.gis.geos import Point
from django.test import TestCase
from haystack import signal_processor
from haystack.backends.elasticsearch_backend import ElasticsearchSearchBackend
from pytz import utc
from django.core.management import call_command

from rest_framework.test import APIClient
from service_directory.api.models import Country, Category, Keyword,\
    Organisation, KeywordCategory, OrganisationCategory, OrganisationKeyword
from service_directory.api.search_indexes import OrganisationIndex


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
    search_backend.update(OrganisationIndex(), [])


class SearchTestCase(TestCase):
    client_class = APIClient

    def tearDown(self):
        call_command('clear_index', interactive=False, verbosity=0)

    @classmethod
    def setUp(cls):
        reset_haystack_index()

        cls.country = Country.objects.create(
            name='South Africa',
            iso_code='ZA'
        )
        cls.country.full_clean()  # force model validation to happen

        cls.category = Category.objects.create(name='Test Category')
        cls.category.full_clean()  # force model validation to happen

        cls.keyword_test = Keyword.objects.create(name='test')
        cls.keyword_test.full_clean()  # force model validation to happen

        kwc = KeywordCategory.objects.create(
            keyword=cls.keyword_test, category=cls.category
        )
        kwc.full_clean()  # force model validation to happen

        cls.keyword_heart = Keyword.objects.create(name='heart')
        cls.keyword_heart.full_clean()  # force model validation to happen

        kwc = KeywordCategory.objects.create(
            keyword=cls.keyword_heart, category=cls.category
        )
        kwc.full_clean()  # force model validation to happen

        cls.keyword_transplant = Keyword.objects.create(name='transplant')
        cls.keyword_transplant.full_clean()  # force model validation to happen

        kwc = KeywordCategory.objects.create(
            keyword=cls.keyword_transplant, category=cls.category
        )
        kwc.full_clean()  # force model validation to happen

        cls.keyword_trauma = Keyword.objects.create(name='trauma')
        cls.keyword_trauma.full_clean()  # force model validation to happen

        kwc = KeywordCategory.objects.create(
            keyword=cls.keyword_trauma, category=cls.category
        )
        kwc.full_clean()  # force model validation to happen

        cls.keyword_hiv = Keyword.objects.create(name='hiv')
        cls.keyword_hiv.full_clean()  # force model validation to happen

        kwc = KeywordCategory.objects.create(
            keyword=cls.keyword_hiv, category=cls.category
        )
        kwc.full_clean()  # force model validation to happen

        cls.keyword_aids = Keyword.objects.create(name='aids')
        cls.keyword_aids.full_clean()  # force model validation to happen

        kwc = KeywordCategory.objects.create(
            keyword=cls.keyword_aids, category=cls.category
        )
        kwc.full_clean()  # force model validation to happen

        cls.keyword_accident = Keyword.objects.create(name='accident')
        cls.keyword_accident.full_clean()  # force model validation to happen

        kwc = KeywordCategory.objects.create(
            keyword=cls.keyword_accident, category=cls.category
        )
        kwc.full_clean()  # force model validation to happen

        cls.org_cbmh = Organisation.objects.create(
            name='Netcare Christiaan Barnard Memorial Hospital',
            country=cls.country,
            location=Point(18.418231, -33.921859, srid=4326)
        )
        cls.org_cbmh.full_clean()  # force model validation to happen

        oc = OrganisationCategory.objects.create(
            organisation=cls.org_cbmh, category=cls.category
        )
        oc.full_clean()  # force model validation to happen

        ok = OrganisationKeyword.objects.create(
            organisation=cls.org_cbmh, keyword=cls.keyword_test
        )
        ok.full_clean()  # force model validation to happen

        ok = OrganisationKeyword.objects.create(
            organisation=cls.org_cbmh, keyword=cls.keyword_heart
        )
        ok.full_clean()  # force model validation to happen

        ok = OrganisationKeyword.objects.create(
            organisation=cls.org_cbmh, keyword=cls.keyword_transplant
        )
        ok.full_clean()  # force model validation to happen

        ok = OrganisationKeyword.objects.create(
            organisation=cls.org_cbmh, keyword=cls.keyword_trauma
        )
        ok.full_clean()  # force model validation to happen

        cls.org_khc = Organisation.objects.create(
            name='Kingsbury Hospital Claremont',
            country=cls.country,
            location=Point(18.469060, -33.986375, srid=4326)
        )
        cls.org_khc.full_clean()  # force model validation to happen

        oc = OrganisationCategory.objects.create(
            organisation=cls.org_khc, category=cls.category
        )
        oc.full_clean()  # force model validation to happen

        ok = OrganisationKeyword.objects.create(
            organisation=cls.org_khc, keyword=cls.keyword_test
        )
        ok.full_clean()  # force model validation to happen

        ok = OrganisationKeyword.objects.create(
            organisation=cls.org_khc, keyword=cls.keyword_hiv
        )
        ok.full_clean()  # force model validation to happen

        ok = OrganisationKeyword.objects.create(
            organisation=cls.org_khc, keyword=cls.keyword_aids
        )
        ok.full_clean()  # force model validation to happen

        cls.org_cmc = Organisation.objects.create(
            name='Constantiaberg Medi Clinic',
            country=cls.country,
            location=Point(18.461260, -34.026629, srid=4326)
        )
        cls.org_cmc.full_clean()  # force model validation to happen

        oc = OrganisationCategory.objects.create(
            organisation=cls.org_cmc, category=cls.category
        )
        oc.full_clean()  # force model validation to happen

        ok = OrganisationKeyword.objects.create(
            organisation=cls.org_cmc, keyword=cls.keyword_test
        )
        ok.full_clean()  # force model validation to happen

        ok = OrganisationKeyword.objects.create(
            organisation=cls.org_cmc, keyword=cls.keyword_trauma
        )
        ok.full_clean()  # force model validation to happen

        ok = OrganisationKeyword.objects.create(
            organisation=cls.org_cmc, keyword=cls.keyword_accident
        )
        ok.full_clean()  # force model validation to happen

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
        response = self.client.get('/api/search/', format='json')

        self.assertEqual(3, len(response.data))

    def test_get_with_search_term_parameter(self):
        response = self.client.get(
            '/api/search/',
            {'search_term': 'test'},
            format='json'
        )
        self.assertEqual(3, len(response.data))

        response = self.client.get(
            '/api/search/',
            {'search_term': 'heart'},
            format='json'
        )
        self.assertEqual(1, len(response.data))

        response = self.client.get(
            '/api/search/',
            {'search_term': 'transplant'},
            format='json'
        )
        self.assertEqual(1, len(response.data))

        response = self.client.get(
            '/api/search/',
            {'search_term': 'trauma'},
            format='json'
        )
        self.assertEqual(2, len(response.data))

        response = self.client.get(
            '/api/search/',
            {'search_term': 'hiv'},
            format='json'
        )
        self.assertEqual(1, len(response.data))

        response = self.client.get(
            '/api/search/',
            {'search_term': 'aids'},
            format='json'
        )
        self.assertEqual(1, len(response.data))

        response = self.client.get(
            '/api/search/',
            {'search_term': 'accident'},
            format='json'
        )
        self.assertEqual(1, len(response.data))

    def test_get_with_location_parameter_with_exact_location(self):
        # -33.921387, 18.424101 - Adderley Street outside Cape Town station
        response = self.client.get(
            '/api/search/', {
                'radius': 100,
                'exact_location': True,
                'location': '-33.921387,18.424101'
            },
            format='json'
        )
        self.assertEqual(3, len(response.data))

        response = self.client.get(
            '/api/search/', {
                'radius': 150,
                'exact_location': True,
                'location': '-32.921387,17.424101'
            },
            format='json'
        )
        # Netcare Christiaan Barnard Memorial Hospital
        # distance: 144.53km
        self.assertEqual(1, len(response.data))

        response = self.client.get(
            '/api/search/', {
                'search_term': 'Netcare',
                'radius': 100,
                'exact_location': True,
                'location': '-32.921387,17.424101'
            },
            format='json'
        )
        self.assertEqual(0, len(response.data))

        response = self.client.get(
            '/api/search/', {
                'search_term': 'testt',
                'radius': 1000,
                'exact_location': True,
                'location': '-32.921387,17.424101'
            },
            format='json'
        )
        self.assertEqual(3, len(response.data))

        response = self.client.get(
            '/api/search/', {
                'search_term': 'testt',
                'radius': 154,
                'exact_location': True,
                'location': '-32.921387,17.424101'
            },
            format='json'
        )
        self.assertEqual(2, len(response.data))

        response = self.client.get(
            '/api/search/', {
                'search_term': 'Hospital',
                'radius': 1000,
                'exact_location': True,
                'location': '-32.921387,17.424101'
            },
            format='json'
        )
        self.assertEqual(2, len(response.data))

        response = self.client.get(
            '/api/search/', {
                'search_term': 'test',
                'radius': 1000,
                'exact_location': True,
                'location': '-32.921387,17.424101'
            },
            format='json'
        )
        self.assertEqual(3, len(response.data))

        response = self.client.get(
            '/api/search/', {
                'search_term': 'Hospital',
                'radius': 150,
                'exact_location': True,
                'location': '-32.921387,17.424101'
            },
            format='json'
        )
        self.assertEqual(1, len(response.data))

    def test_get_with_location_parameter(self):
        # -33.921387, 18.424101 - Adderley Street outside Cape Town station
        response = self.client.get(
            '/api/search/',
            {'location': '-33.921387,18.424101'},
            format='json'
        )

        # we should get all 3 organisations, ordered from closest to farthest
        # Christiaan Barnard Memorial Hospital is closest, followed by
        # Kingsbury Hospital Claremont and then Constantiaberg Medi Clinic
        self.assertEqual(3, len(response.data))

        # Netcare Christiaan Barnard Memorial Hospital
        self.assertEqual(self.org_cbmh.name, response.data[0]['name'])
        self.assertListEqual([kw.name for kw in self.org_cbmh.keywords.all()],
                             response.data[0]['keywords'])

        self.assertEqual(self.org_khc.name, response.data[1]['name'])
        self.assertListEqual([kw.name for kw in self.org_khc.keywords.all()],
                             response.data[1]['keywords'])

        self.assertEqual(self.org_cmc.name, response.data[2]['name'])
        self.assertListEqual([kw.name for kw in self.org_cmc.keywords.all()],
                             response.data[2]['keywords'])

    def test_get_with_location_parameter_org_with_no_location(self):
        self.org_prkc = Organisation.objects.create(
            name='Praekelt Clinic',
            country=Country.objects.get(iso_code='ZA')
        )
        self.org_prkc.full_clean()  # force model validation to happen

        oc = OrganisationCategory.objects.create(
            organisation=self.org_prkc,
            category=Category.objects.get(name='Test Category')
        )
        oc.full_clean()  # force model validation to happen

        keyword_test = Keyword.objects.get(name='test')
        ok = OrganisationKeyword.objects.create(
            organisation=self.org_prkc, keyword=keyword_test
        )
        ok.full_clean()  # force model validation to happen
        signal_processor.flush_changes()

        # -33.921387, 18.424101 - Adderley Street outside Cape Town station
        response = self.client.get(
            '/api/search/',
            {'location': '-33.921387,18.424101'},
            format='json'
        )

        # we should get all 3 organisations, ordered from closest to farthest
        # Christiaan Barnard Memorial Hospital is closest, followed by
        # Kingsbury Hospital Claremont and then Constantiaberg Medi Clinic
        self.assertEqual(4, len(response.data))

        # Netcare Christiaan Barnard Memorial Hospital
        self.assertEqual(self.org_cbmh.name, response.data[0]['name'])
        self.assertListEqual([kw.name for kw in self.org_cbmh.keywords.all()],
                             response.data[0]['keywords'])

        self.assertEqual(self.org_khc.name, response.data[1]['name'])
        self.assertListEqual([kw.name for kw in self.org_khc.keywords.all()],
                             response.data[1]['keywords'])

        self.assertEqual(self.org_cmc.name, response.data[2]['name'])
        self.assertListEqual([kw.name for kw in self.org_cmc.keywords.all()],
                             response.data[2]['keywords'])

        self.assertEqual(self.org_prkc.name, response.data[3]['name'])
        self.assertIsNone(response.data[3]['distance'])

    def test_get_with_search_term_and_location_parameters(self):
        # -33.921387, 18.424101 - Adderley Street outside Cape Town station
        response = self.client.get(
            '/api/search/',
            {
                'search_term': 'trauma',
                'location': '-33.921387,18.424101'
            },
            format='json'
        )

        # we should get 2 organisations, ordered from closest to farthest
        # Christiaan Barnard Memorial Hospital is closest
        self.assertEqual(2, len(response.data))

        self.assertEqual(self.org_cbmh.name, response.data[0]['name'])
        self.assertListEqual([kw.name for kw in self.org_cbmh.keywords.all()],
                             response.data[0]['keywords'])

        self.assertEqual(self.org_cmc.name, response.data[1]['name'])
        self.assertListEqual([kw.name for kw in self.org_cmc.keywords.all()],
                             response.data[1]['keywords'])

    def test_fuzzy_matching(self):
        # match on keyword and category name
        response = self.client.get(
            '/api/search/',
            {
                'search_term': 'testt'
            },
            format='json'
        )

        self.assertEqual(3, len(response.data))

        # match on keyword name
        response = self.client.get(
            '/api/search/',
            {
                'search_term': 'aid'
            },
            format='json'
        )

        self.assertEqual(1, len(response.data))
        self.assertEqual(self.org_khc.name, response.data[0]['name'])

        # match on category name
        response = self.client.get(
            '/api/search/',
            {
                'search_term': 'category'
            },
            format='json'
        )

        self.assertEqual(3, len(response.data))

        # match on org name
        response = self.client.get(
            '/api/search/',
            {
                'search_term': 'med'
            },
            format='json'
        )

        self.assertEqual(1, len(response.data))
        self.assertEqual(self.org_cmc.name, response.data[0]['name'])

        # match on org name
        response = self.client.get(
            '/api/search/',
            {
                'search_term': 'hospice'
            },
            format='json'
        )

        self.assertEqual(2, len(response.data))


class OrganisationDetailTestCase(TestCase):
    client_class = APIClient

    @classmethod
    def setUpTestData(cls):
        cls.country = Country.objects.create(
            name='South Africa',
            iso_code='ZA'
        )
        cls.country.full_clean()  # force model validation to happen

        cls.category = Category.objects.create(name='Test Category')
        cls.category.full_clean()  # force model validation to happen

        cls.keyword = Keyword.objects.create(name='test')
        cls.keyword.full_clean()  # force model validation to happen

        kwc = KeywordCategory.objects.create(
            keyword=cls.keyword, category=cls.category
        )
        kwc.full_clean()  # force model validation to happen

        cls.org = Organisation.objects.create(
            name='Test Organisation',
            country=cls.country,
            location=Point(18.505496, -33.891937, srid=4326)
        )
        cls.org.full_clean()  # force model validation to happen

        oc = OrganisationCategory.objects.create(
            organisation=cls.org, category=cls.category
        )
        oc.full_clean()  # force model validation to happen

        ok = OrganisationKeyword.objects.create(
            organisation=cls.org, keyword=cls.keyword
        )
        ok.full_clean()  # force model validation to happen

    def test_get(self):
        response = self.client.get(
            '/api/organisation/{0}/'.format(self.org.id),
            format='json'
        )

        expected_response_content = '''
            {
                "id":%s,
                "name":"%s",
                "about":"",
                "address":"",
                "telephone":"",
                "emergency_telephone":"",
                "email":"",
                "web":"",
                "verified_as":"",
                "age_range_min":null,
                "age_range_max":null,
                "opening_hours":"",
                "location":"%s",
                "country":
                    {
                        "id":%s,
                        "name":"%s",
                        "iso_code":"%s"
                    },
                "categories":[
                    {
                        "id":%s,
                        "name":"%s",
                        "show_on_home_page":%s
                    }
                ],
                "keywords":[
                    {
                        "id":%s,
                        "name":"%s",
                        "show_on_home_page":%s,
                        "categories":[
                            %s
                        ]
                    }
                ],
                "facility_code":""
            }
        ''' % (self.org.id, self.org.name, self.org.location,
               self.country.id, self.country.name, self.country.iso_code,
               self.category.id, self.category.name,
               str(self.category.show_on_home_page).lower(),
               self.keyword.id, self.keyword.name,
               str(self.keyword.show_on_home_page).lower(), self.category.id)

        self.assertJSONEqual(response.content, expected_response_content)


class OrganisationReportIncorrectInformationTestCase(TestCase):
    client_class = APIClient

    @classmethod
    def setUpTestData(cls):
        cls.country = Country.objects.create(
            name='South Africa',
            iso_code='ZA'
        )
        cls.country.full_clean()  # force model validation to happen

        cls.org = Organisation.objects.create(
            name='Test Organisation',
            country=cls.country,
            location=Point(18.505496, -33.891937, srid=4326)
        )
        cls.org.full_clean()  # force model validation to happen

    def test_post(self):
        response = self.client.post(
            '/api/organisation/{0}/report/'.format(self.org.id),
            {
                'contact_details': True
            },
            format='json'
        )

        pattern = re.compile(r'(\"reported_at\":)'
                             r'\"(\d{4}-\d{2}-\d{2}T'
                             r'\d{2}:\d{2}:\d{2}.\d{6}Z)\",')

        reported_at_str = pattern.search(response.content).group(2)
        reported_at = parse(reported_at_str)

        # replace the reported_at value in the response content so that we can
        # assertJSONEqual
        modified_response_content = pattern.sub(r'\1"replaced",',
                                                response.content)

        # be aware that the returned ID may change if you add more test methods
        # to this test case
        expected_response_content = '''
            {
                "id":1,
                "reported_at":"replaced",
                "contact_details":true,
                "address":null,
                "trading_hours":null,
                "other":null,
                "other_detail":"",
                "organisation":%s
            }
        ''' % (self.org.id,)

        self.assertJSONEqual(modified_response_content,
                             expected_response_content)

        # assert reported_at separately
        self.assertAlmostEqual(
            datetime.now(utc),
            reported_at,
            delta=timedelta(seconds=10)
        )


class OrganisationRateTestCase(TestCase):
    client_class = APIClient

    @classmethod
    def setUpTestData(cls):
        cls.country = Country.objects.create(
            name='South Africa',
            iso_code='ZA'
        )
        cls.country.full_clean()  # force model validation to happen

        cls.org = Organisation.objects.create(
            name='Test Organisation',
            country=cls.country,
            location=Point(18.505496, -33.891937, srid=4326)
        )
        cls.org.full_clean()  # force model validation to happen

    def test_post(self):
        response = self.client.post(
            '/api/organisation/{0}/rate/'.format(self.org.id),
            {
                'rating': 'poor'
            },
            format='json'
        )

        pattern = re.compile(r'(\"rated_at\":)'
                             r'\"(\d{4}-\d{2}-\d{2}T'
                             r'\d{2}:\d{2}:\d{2}.\d{6}Z)\",')

        rated_at_str = pattern.search(response.content).group(2)
        rated_at = parse(rated_at_str)

        # replace the rated_at value in the response content so that we can
        # assertJSONEqual
        modified_response_content = pattern.sub(r'\1"replaced",',
                                                response.content)

        # be aware that the returned ID may change if you add more test methods
        # to this test case
        expected_response_content = '''
            {
                "id":1,
                "rated_at":"replaced",
                "rating":"poor",
                "organisation":%s
            }
        ''' % (self.org.id,)

        self.assertJSONEqual(modified_response_content,
                             expected_response_content)

        # assert rated_at separately
        self.assertAlmostEqual(
            datetime.now(utc),
            rated_at,
            delta=timedelta(seconds=10)
        )


class HomePageCategoryKeywordGroupingTestCase(TestCase):
    client_class = APIClient

    @classmethod
    def setUpTestData(cls):
        cls.category_1 = Category.objects.create(
            name='Test Category 1',
            show_on_home_page=True
        )
        cls.category_1.full_clean()  # force model validation to happen

        cls.category_2 = Category.objects.create(
            name='Test Category 2',
            show_on_home_page=True
        )
        cls.category_2.full_clean()  # force model validation to happen

        cls.category_3 = Category.objects.create(
            name='Test Category 3',
            show_on_home_page=True
        )
        cls.category_3.full_clean()  # force model validation to happen

        cls.category_4 = Category.objects.create(
            name='Test Category 4',
            show_on_home_page=False
        )
        cls.category_4.full_clean()  # force model validation to happen

        cls.keyword_1 = Keyword.objects.create(
            name='test1',
            show_on_home_page=True
        )
        cls.keyword_1.full_clean()  # force model validation to happen

        kwc = KeywordCategory.objects.create(
            keyword=cls.keyword_1, category=cls.category_1
        )
        kwc.full_clean()  # force model validation to happen

        cls.keyword_2 = Keyword.objects.create(
            name='test2',
            show_on_home_page=False
        )
        cls.keyword_2.full_clean()  # force model validation to happen

        kwc = KeywordCategory.objects.create(
            keyword=cls.keyword_2, category=cls.category_2
        )
        kwc.full_clean()  # force model validation to happen

        cls.keyword_3 = Keyword.objects.create(
            name='test3',
            show_on_home_page=True
        )
        cls.keyword_3.full_clean()  # force model validation to happen

        kwc = KeywordCategory.objects.create(
            keyword=cls.keyword_3, category=cls.category_3
        )
        kwc.full_clean()  # force model validation to happen

        kwc = KeywordCategory.objects.create(
            keyword=cls.keyword_3, category=cls.category_4
        )
        kwc.full_clean()  # force model validation to happen

        cls.keyword_4 = Keyword.objects.create(
            name='test4',
            show_on_home_page=True
        )
        cls.keyword_4.full_clean()  # force model validation to happen

        kwc = KeywordCategory.objects.create(
            keyword=cls.keyword_4, category=cls.category_4
        )
        kwc.full_clean()  # force model validation to happen

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
        cls.category_1.full_clean()  # force model validation to happen
        cls.category_2 = Category.objects.create(
            name='Test Category 2'
        )
        cls.category_2.full_clean()  # force model validation to happen

        cls.cat1kw1 = Keyword.objects.create(
            name='cat1kw1'
        )
        cls.cat1kw1.full_clean()  # force model validation to happen

        kwc = KeywordCategory.objects.create(
            keyword=cls.cat1kw1, category=cls.category_1
        )
        kwc.full_clean()  # force model validation to happen

        cls.cat1kw2 = Keyword.objects.create(
            name='cat1kw2'
        )
        cls.cat1kw2.full_clean()  # force model validation to happen

        kwc = KeywordCategory.objects.create(
            keyword=cls.cat1kw2, category=cls.category_1
        )
        kwc.full_clean()  # force model validation to happen

        cls.cat2kw1 = Keyword.objects.create(
            name='cat2kw1'
        )
        cls.cat2kw1.full_clean()  # force model validation to happen

        kwc = KeywordCategory.objects.create(
            keyword=cls.cat2kw1, category=cls.category_2
        )
        kwc.full_clean()  # force model validation to happen

        cls.cat2kw2 = Keyword.objects.create(
            name='cat2kw2'
        )
        cls.cat2kw2.full_clean()  # force model validation to happen

        kwc = KeywordCategory.objects.create(
            keyword=cls.cat2kw2, category=cls.category_2
        )
        kwc.full_clean()  # force model validation to happen

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
