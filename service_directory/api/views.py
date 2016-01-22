from django.contrib.gis.geos import Point
from haystack.query import SearchQuerySet
from rest_framework.generics import RetrieveAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from service_directory.api.models import Service

from service_directory.api.serializers import ServiceSerializer, \
    ServiceSummarySerializer


class ServiceLookupView(APIView):
    """
    Query services by keyword
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
            sqs = sqs.filter(content=keyword)

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

        services = zip(*service_distance_tuples)[0]

        serializer = ServiceSummarySerializer(services, many=True)

        return Response(serializer.data)


class ServiceDetail(RetrieveAPIView):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer
