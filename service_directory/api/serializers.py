from collections import OrderedDict

from models import Service, Organisation, Category, Keyword, \
    ServiceIncorrectInformationReport, ServiceRating
from rest_framework import serializers


class HomePageCategoryKeywordGroupingSerializer(serializers.ModelSerializer):
    keywords = serializers.StringRelatedField(source='filtered_keywords',
                                              many=True)

    class Meta:
        model = Category
        fields = ('name', 'keywords')


class KeywordSerializer(serializers.ModelSerializer):
    class Meta:
        model = Keyword


class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        # Swagger does not deal well with NestedSerializer (ie: depth attr)
        # https://github.com/marcgibbons/django-rest-swagger/issues/398
        # Explicitly defining the descendant serializers would solve it
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
        fields = ('id', 'name', 'keywords', 'organisation', 'distance')

    # Note: Strictly speaking nothing above this comment is required for the
    # serializer to work, however it helps Swagger to work out what the
    # response will look like

    def to_representation(self, instance):
        d = OrderedDict()

        d['id'] = instance.id
        d['name'] = instance.name
        d['keywords'] = [keyword.name for keyword in instance.keywords.all()]
        d['organisation'] = OrganisationSummarySerializer(
            instance.organisation
        ).data
        d['distance'] = instance.distance if hasattr(instance, 'distance')\
            else None

        return d


class ServiceIncorrectInformationReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceIncorrectInformationReport
        read_only_fields = ('service',)


class ServiceRatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceRating
        read_only_fields = ('service',)


class ServiceSendSMSRequestSerializer(serializers.Serializer):
    cell_number = serializers.CharField()
    service_url = serializers.URLField()


class ServiceSendSMSResponseSerializer(serializers.Serializer):
    result = serializers.BooleanField()
