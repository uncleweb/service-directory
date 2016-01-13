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
        response_serializer: ServiceSerializer
    """
    def get(self, request):
        if 'keyword' in request.query_params:
            q = request.query_params['keyword']
            q.strip()

            services = Service.objects.filter(keywords__icontains=q)
            serializer = ServiceSerializer(services, many=True)
            data = serializer.data

            return Response(data)

        return Response()
