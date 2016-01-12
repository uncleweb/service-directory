from rest_framework.renderers import TemplateHTMLRenderer, JSONRenderer

from rest_framework.response import Response
from rest_framework.views import APIView

from service_directory.api.models import Service
from service_directory.api.serializers import ServiceSerializer


class ServiceLookupView(APIView):
    renderer_classes = (TemplateHTMLRenderer, JSONRenderer)
    template_name = 'service_lookup.html'

    def get(self, request):

        data = {}

        if 'q' in request.query_params:
            q = request.query_params['q']
            q.strip()

            services = Service.objects.filter(keywords__icontains=q)
            serializer = ServiceSerializer(services, many=True)
            data = serializer.data

        if request.accepted_renderer.format == 'html':
            context = {'response': data}
            return Response(context)

        return Response(data)


# Default browsable API rendering without a form
# class ServiceLookupView(APIView):
#     def get(self, request):
#         if 'q' in request.query_params:
#             q = request.query_params['q']
#             q.strip()
#
#             services = Service.objects.filter(keywords__icontains=q)
#             serializer = ServiceSerializer(services, many=True)
#             data = serializer.data
#
#             return Response(data)
#
#         return Response()
