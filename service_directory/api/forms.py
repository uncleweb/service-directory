from django import forms
from django.contrib.gis.geos import Point
from service_directory.api.models import Organisation


class OrganisationModelForm(forms.ModelForm):
    class Meta:
        model = Organisation
        fields = '__all__'

    location_coords = forms.CharField(
        required=False,
        label='Location coordinates',
        help_text='Enter coordinates as latitude,longitude. '
        'Note that entering coordinates here overrides any location set via'
        ' the map.'
    )

    def save(self, commit=True):
        location_coords = self.cleaned_data.get('location_coords', None)

        if location_coords:
            lat, lng = location_coords.split(',')
            lat = float(lat)
            lng = float(lng)
            point = Point(lng, lat, srid=4326)

            self.instance.location = point

        return super(OrganisationModelForm, self).save(commit=commit)
