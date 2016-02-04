from django import forms
from django.contrib.gis.geos import Point
from django.core.exceptions import ValidationError
from service_directory.api.models import Organisation


class OrganisationModelForm(forms.ModelForm):
    class Meta:
        model = Organisation
        fields = '__all__'

    location_coords = forms.CharField(
        required=False,
        label='Location coordinates',
        help_text='Enter coordinates as latitude,longitude.'
        ' Note that entering coordinates here overrides any location set via'
        ' the map.'
    )

    def clean_location_coords(self):
        location_coords = self.cleaned_data.get('location_coords')
        if location_coords:
            try:
                lat, lng = location_coords.split(',')
                lat = float(lat)
                lng = float(lng)
                point = Point(lng, lat, srid=4326)
            except ValueError:
                raise ValidationError(
                    "Invalid coordinates. Coordinates must be comma-separated"
                    " latitude,longitude decimals, eg: -33.921124,18.417313"
                )

            return point
        return location_coords

    def clean(self):
        super(OrganisationModelForm, self).clean()

        location_coords = self.cleaned_data.get('location_coords')

        # only override location if location_coords is a valid Point and does
        # not match the current location
        if isinstance(location_coords, Point) and \
                location_coords != self.instance.location:

            self.cleaned_data['location'] = self.cleaned_data.get(
                'location_coords'
            )

            # if location_coords is a valid Point then we can ignore errors
            # about the location field (eg: 'Delete all Features' is used to
            # remove the map marker but valid coordinates are entered into
            # the location_coords field)
            if self.has_error('location'):
                del self.errors['location']
