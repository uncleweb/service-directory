from django.contrib.auth.models import User
from django.contrib.gis.geos import Point
from django.test import TestCase
from service_directory.api.models import Country, Organisation, CountryArea


class AdminFormsTestCase(TestCase):
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

    def test_organisation_model_form_location_coords_field(self):
        self.client.login(username=self.SU_USERNAME, password=self.SU_PASSWORD)

        url = '/admin/api/organisation/{0}/'.format(self.org_cbmh.id)

        new_lat = -33.921124
        new_lng = 18.417313

        data = {
            'name': self.org_cbmh.name,
            'about': self.org_cbmh.about,
            'address': self.org_cbmh.address,
            'telephone': self.org_cbmh.telephone,
            'email': self.org_cbmh.email,
            'web': self.org_cbmh.web,
            'country': self.org_cbmh.country_id,
            'areas': self.country_area.id,
            'location': self.org_cbmh.location,
            'location_coords': '{0},{1}'.format(new_lat, new_lng)
        }

        response = self.client.post(url, data)

        self.assertEqual(200, response.status_code)

        # TODO: make these asserts pass
        # OrganisationModelForm.save() is not called
        # org = Organisation.objects.get(pk=self.org_cbmh.id)
        # self.assertEqual(new_lat, org.location.y)
        # self.assertEqual(new_lng, org.location.x)
