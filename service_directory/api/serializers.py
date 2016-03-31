from collections import OrderedDict

from models import Organisation, Category, Keyword
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


# class ServiceSerializer(serializers.ModelSerializer):
#     class Meta:
#         # Swagger does not deal well with NestedSerializer (ie: depth attr)
#         # https://github.com/marcgibbons/django-rest-swagger/issues/398
#         # Explicitly defining the descendant serializers would solve it
#         model = Service
#         depth = 1


class OrganisationSummarySerializer(serializers.ModelSerializer):
    distance = serializers.CharField()

    class Meta:
        model = Organisation
        fields = ('id', 'name', 'address', 'keywords', 'distance')

    # Note: Strictly speaking nothing above this comment is required for the
    # serializer to work, however it helps Swagger to work out what the
    # response will look like

    def to_representation(self, instance):
        d = OrderedDict()

        d['id'] = instance.id
        d['name'] = instance.name
        d['address'] = instance.address
        d['keywords'] = [keyword.name for keyword in instance.keywords.all()]
        d['distance'] = instance.distance if hasattr(instance, 'distance')\
            else None

        return d


# class ServiceIncorrectInformationReportSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = ServiceIncorrectInformationReport
#         read_only_fields = ('service',)
#
#
# class ServiceRatingSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = ServiceRating
#         read_only_fields = ('service',)


class ServiceSendSMSRequestSerializer(serializers.Serializer):
    # TODO: add validation for cell_number field
    # http://www.django-rest-framework.org/api-guide/serializers/#validation
    cell_number = serializers.CharField()
    service_url = serializers.URLField()
    your_name = serializers.CharField(required=False)


class ServiceSendSMSResponseSerializer(serializers.Serializer):
    result = serializers.BooleanField()
