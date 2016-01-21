from collections import OrderedDict

from rest_framework import serializers
from models import Service, Organisation


class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        depth = 1


class OrganisationSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Organisation
        fields = ('id', 'name', 'address')


class ServiceSummarySerializer(serializers.ModelSerializer):
    organisation = OrganisationSummarySerializer()
    distance = serializers.CharField()

    class Meta:
        model = Service
        fields = ('id', 'keywords', 'organisation', 'distance')

    # Note: Strictly speaking nothing above this comment is required for the
    # serializer to work, however it helps swagger to work out what the
    # response will look like

    def to_representation(self, instance):
        d = OrderedDict()

        d['id'] = instance.id
        d['keywords'] = instance.keywords
        d['organisation'] = OrganisationSummarySerializer(
            instance.organisation
        ).data
        d['distance'] = instance.distance if hasattr(instance, 'distance')\
            else None

        return d
