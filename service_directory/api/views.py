from django.contrib.gis.geos import Point
from django.db.models.query import Prefetch
from haystack.query import SearchQuerySet
from rest_framework.generics import RetrieveAPIView, ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from service_directory.api.models import Service, Keyword, Category

from service_directory.api.serializers import ServiceSerializer, \
    ServiceSummarySerializer, HomePageCategoryKeywordGroupingSerializer, \
    KeywordSerializer


class HomePageCategoryKeywordGrouping(APIView):
    """
    Retrieve keywords grouped by category for the home page
    ---
    GET:
        response_serializer: HomePageCategoryKeywordGroupingSerializer
    """
    def get(self, request):
        filtered_keyword_queryset = Keyword.objects.filter(
            show_on_home_page=True
        )

        home_page_categories_with_keywords = Category.objects.filter(
            show_on_home_page=True
        ).prefetch_related(
            Prefetch(
                'keyword_set',
                queryset=filtered_keyword_queryset,
                to_attr='filtered_keywords'
            )
        )

        # exclude categories that don't have any keywords associated
        home_page_categories_with_keywords = [
            category for category in home_page_categories_with_keywords
            if category.filtered_keywords
        ]

        serializer = HomePageCategoryKeywordGroupingSerializer(
            home_page_categories_with_keywords, many=True
        )
        return Response(serializer.data)


class KeywordList(ListAPIView):
    """
    List Keywords, optionally filtering by category
    ---
    GET:
        parameters:
            - name: category
              type: string
              paramType: query
              allowMultiple: true
    """
    serializer_class = KeywordSerializer

    def get_queryset(self):
        queryset = Keyword.objects.all()

        category_list = self.request.query_params.getlist('category')

        if category_list:
            queryset = queryset.filter(categories__name__in=category_list)

        return queryset


class ServiceLookup(APIView):
    """
    Query services by keyword and/or location
    ---
    GET:
        parameters:
            - name: keyword
              type: string
              paramType: query
            - name: near
              description: latitude,longitude
              type: string
              paramType: query
        response_serializer: ServiceSummarySerializer
    """
    def get(self, request):
        point = None
        keyword = None

        if 'near' in request.query_params:
            latlng = request.query_params['near'].strip()
            lat, lng = latlng.split(',')
            lat = float(lat)
            lng = float(lng)
            point = Point(lng, lat, srid=4326)

        if 'keyword' in request.query_params:
            keyword = request.query_params['keyword'].strip()

        sqs = SearchQuerySet()

        if keyword:
            sqs = sqs.filter(text=keyword)

        if point:
            sqs = sqs.distance('location', point).order_by('distance')

        # fetch all result objects and limit to 20 results
        sqs = sqs.load_all()[:20]

        service_distance_tuples = [
            (
                result.object, result.distance if hasattr(result, 'distance')
                else None
            )
            for result in sqs
        ]

        for service, distance in service_distance_tuples:
            if distance is not None:
                service.distance = '{0:.2f}km'.format(distance.km)

        if service_distance_tuples:
            services = zip(*service_distance_tuples)[0]
            serializer = ServiceSummarySerializer(services, many=True)
            return Response(serializer.data)

        return Response([])


class ServiceDetail(RetrieveAPIView):
    """
    Retrieve service details
    """
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer
