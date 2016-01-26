from django.contrib.gis.geos import Point
from django.db.models.query import Prefetch
from haystack.query import SearchQuerySet
from rest_framework.generics import RetrieveAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from service_directory.api.models import Service, Keyword, Category

from service_directory.api.serializers import ServiceSerializer, \
    ServiceSummarySerializer


class HomePageCategoryKeywordGrouping(APIView):
    """
    Retrieve keywords grouped by category for the home page
    """
    def get(self, request):
        filtered_keyword_queryset = Keyword.objects.filter(
            show_on_home_page=True
        )

        home_page_categories = Category.objects.filter(
            show_on_home_page=True
        ).prefetch_related(
            Prefetch(
                'keyword_set',
                queryset=filtered_keyword_queryset,
                to_attr='filtered_keywords'
            )
        )[:5]

        category_grouped_keywords = {
            'categories': []
        }

        for category in home_page_categories:
            if not category.filtered_keywords:
                continue

            category_grouped_keywords['categories'].append({
                'name': category.name,
                'keywords': [
                    keyword.name for keyword in category.filtered_keywords[:5]
                ]
            })

        return Response(category_grouped_keywords)


class ServiceLookupView(APIView):
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
