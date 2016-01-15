from django.contrib.gis.geos import Point
from rest_framework.response import Response
from rest_framework.views import APIView

from service_directory.api.models import Service
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

        services = Service.objects.all()

        if keyword:
            services = services.filter(keywords__icontains=keyword)

        if point:
            # TODO: investigate adding distance to serialized output
            services = services.distance(point, field_name='organisation__location').order_by('distance')

        # limit to 20 results
        services = services[:20]

        serializer = ServiceSerializer(services, many=True)

        return Response(serializer.data)
