from rest_framework import status

from rest_framework.response import Response
from rest_framework.views import APIView

from service_directory.api.models import Service
from service_directory.api.serializers import ServiceSerializer


class ServiceLookup(APIView):
    def get(self, request):
        if 'q' not in request.query_params:
            return Response(status.HTTP_400_BAD_REQUEST)

        q = request.query_params['q']
        q.strip()

        services = Service.objects.filter(keywords__icontains=q)
        serializer = ServiceSerializer(services, many=True)

        return Response(serializer.data)
