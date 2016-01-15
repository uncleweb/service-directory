from django.contrib.gis.geos import Point
from haystack.query import SearchQuerySet
from rest_framework.response import Response
from rest_framework.views import APIView

from service_directory.api.serializers import ServiceSerializer


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
        response_serializer: ServiceSerializer
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
            # TODO: investigate adding distance to serialized output
            sqs = sqs.distance('location', point).order_by('-distance')

        # fetch all result objects and limit to 20 results
        sqs = sqs.load_all()[:20]

        services = [result.object for result in sqs]

        serializer = ServiceSerializer(services, many=True)

        return Response(serializer.data)
