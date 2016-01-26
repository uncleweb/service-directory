from django.contrib.auth.models import User
from django.contrib.gis.geos import Point
from django.test import TestCase
from service_directory.api.models import Country, Organisation, CountryArea


class OrganisationModelFormTestCase(TestCase):
    SU_USERNAME = 'test'
    SU_PASSWORD = 'test'

    @classmethod
    def setUpTestData(cls):
        User.objects.create_superuser(
            cls.SU_USERNAME, 'test@test.com', cls.SU_PASSWORD
        )

        cls.country = Country.objects.create(
            name='South Africa',
            iso_code='ZA'
        )

        cls.country_area = CountryArea.objects.create(
            name='Western Cape',
            level=CountryArea.AREA_LEVELS[0][0],  # Province/State
            country=cls.country
        )

        cls.org_cbmh = Organisation.objects.create(
            name='Netcare Christiaan Barnard Memorial Hospital',
            country=cls.country,
            location=Point(18.418231, -33.921859, srid=4326)
        )
        cls.org_cbmh.areas.add(cls.country_area)

        cls.api_url = '/admin/api/organisation/{0}/'.format(cls.org_cbmh.id)

    def setUp(self):
        self.client.login(username=self.SU_USERNAME, password=self.SU_PASSWORD)

    def get_post_payload_for_test_organisation(self):
        data = {
            'name': self.org_cbmh.name,
            'about': self.org_cbmh.about,
            'address': self.org_cbmh.address,
            'telephone': self.org_cbmh.telephone,
            'email': self.org_cbmh.email,
            'web': self.org_cbmh.web,
            'country': self.org_cbmh.country_id,
            'areas': self.country_area.id,
            'location': self.org_cbmh.location
        }
        return data

    def test_location_coords_field_overrides_map_location(self):
        new_lat = -33.921124
        new_lng = 18.417313

        data = self.get_post_payload_for_test_organisation()
        data['location_coords'] = '{0},{1}'.format(new_lat, new_lng)

        response = self.client.post(self.api_url, data)

        self.assertEqual(302, response.status_code)
        self.assertTrue(
            response._headers['location'][1].endswith(
                '/admin/api/organisation/'
            )
        )

        org = Organisation.objects.get(pk=self.org_cbmh.id)
        self.assertEqual(new_lat, org.location.y)
        self.assertEqual(new_lng, org.location.x)

    def test_location_coords_field_validation(self):
        data = self.get_post_payload_for_test_organisation()
        data['location_coords'] = '123abc'

        response = self.client.post(self.api_url, data)

        self.assertContains(response, 'Invalid coordinates')

    def test_map_location_required_if_location_coords_field_empty(self):
        data = self.get_post_payload_for_test_organisation()
        del data['location']

        response = self.client.post(self.api_url, data)

        self.assertContains(response, 'No geometry value provided')

    def test_map_location_not_required_if_location_coords_supplied(self):
        new_lat = -33.921124
        new_lng = 18.417313

        data = self.get_post_payload_for_test_organisation()
        del data['location']
        data['location_coords'] = '{0},{1}'.format(new_lat, new_lng)

        response = self.client.post(self.api_url, data)

        self.assertEqual(302, response.status_code)
        self.assertTrue(
            response._headers['location'][1].endswith(
                '/admin/api/organisation/'
            )
        )
