import logging

from UniversalAnalytics import Tracker
from django.conf import settings
from django.contrib.gis.geos import Point
from django.db.models.query import Prefetch
from django.http import Http404
from go_http import HttpApiSender
from rest_framework import status
from rest_framework.generics import RetrieveAPIView, ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from service_directory.api.haystack_elasticsearch_raw_query.\
    custom_elasticsearch import ConfigurableSearchQuerySet
from service_directory.api.models import Keyword, Category, Organisation
from service_directory.api.serializers import\
    HomePageCategoryKeywordGroupingSerializer, \
    KeywordSerializer, ServiceSendSMSRequestSerializer, \
    ServiceSendSMSResponseSerializer, OrganisationSummarySerializer

google_analytics_tracker = Tracker.create(
    settings.GOOGLE_ANALYTICS_TRACKING_ID,
    client_id='SERVICE-DIRECTORY-API'
)


def send_ga_tracking_event(path, category, action, label):
    try:
        google_analytics_tracker.send(
            'event',
            path=path,
            ec=category,
            ea=action,
            el=label
        )
    except:
        logging.warn("Google Analytics call failed", exc_info=True)


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
    List keywords, optionally filtering by category
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

            if queryset:
                # although this endpoint accepts a list of categories we only
                # send a tracking event for the first one as generally only one
                # will be supplied (and we don't want to block the response
                # because of a large number of tracking calls)
                send_ga_tracking_event(
                    self.request._request.path, 'View', 'KeywordsInCategory',
                    category_list[0]
                )

        return queryset


class Search(APIView):
    """
    Search for organisations by search term and/or location.
    If location coordinates are supplied then results are ordered ascending
    by distance.
    ---
    GET:
        parameters:
            - name: search_term
              type: string
              paramType: query
            - name: location
              description: latitude,longitude
              type: string
              paramType: query
            - name: place_name
              description: only used for analytics purposes
              type: string
              paramType: query
        response_serializer: OrganisationSummarySerializer
    """
    def get(self, request):
        search_term = None
        point = None
        place_name = None

        if 'search_term' in request.query_params:
            search_term = request.query_params['search_term'].strip()

        if 'location' in request.query_params:
            latlng = request.query_params['location'].strip()
            lat, lng = latlng.split(',')
            lat = float(lat)
            lng = float(lng)
            point = Point(lng, lat, srid=4326)

        if 'place_name' in request.query_params:
            place_name = request.query_params['place_name'].strip()

        send_ga_tracking_event(
            request._request.path,
            'Search',
            search_term or '',
            place_name or ''
        )

        sqs = ConfigurableSearchQuerySet().models(Organisation)

        if search_term:
            query = {
                "match": {
                    "text": {
                        "query": search_term,
                        "fuzziness": "AUTO"
                    }
                }
            }
            sqs = sqs.custom_query(query)

        if point:
            sqs = sqs.distance('location', point).order_by('distance')

        # fetch all result objects and limit to 20 results
        sqs = sqs.load_all()[:20]

        organisation_distance_tuples = []
        try:
            organisation_distance_tuples = [
                (
                    result.object,
                    result.distance if hasattr(result, 'distance') else None
                )
                for result in sqs
            ]
        except AttributeError:
            logging.warn('The ElasticSearch index is likely out of sync with'
                         ' the database. You should run the `rebuild_index`'
                         ' management command.')

        for organisation, distance in organisation_distance_tuples:
            if distance is not None:
                organisation.distance = '{0:.2f}km'.format(distance.km)

        if organisation_distance_tuples:
            services = zip(*organisation_distance_tuples)[0]
            serializer = OrganisationSummarySerializer(services, many=True)
            return Response(serializer.data)

        return Response([])


# class ServiceDetail(RetrieveAPIView):
#     """
#     Retrieve service details
#     """
#     queryset = Service.objects.all()
#     serializer_class = ServiceSerializer
#
#     def get(self, request, *args, **kwargs):
#         response = super(ServiceDetail, self).get(request, *args, **kwargs)
#
#         if response and response.data:
#             try:
#                 service_name = response.data['name']
#                 organisation_name = response.data['organisation']['name']
#                 label = '{0} ({1})'.format(service_name, organisation_name)
#
#                 send_ga_tracking_event(
#                     request._request.path, 'View', 'Service', label
#                 )
#             except (KeyError, TypeError):
#                 logging.warn("Did not find expected data in response to make"
#                              " Google Analytics call", exc_info=True)
#
#         return response


# class ServiceReportIncorrectInformation(APIView):
#     """
#     Report incorrect information for a service
#     ---
#     POST:
#          serializer: ServiceIncorrectInformationReportSerializer
#     """
#     def post(self, request, *args, **kwargs):
#         service_id = int(kwargs.pop('pk'))
#
#         try:
#             service = Service.objects.get(id=service_id)
#         except Service.DoesNotExist:
#             raise Http404
#
#         serializer = ServiceIncorrectInformationReportSerializer(
#             data=request.data
#         )
#
#         serializer.is_valid(raise_exception=True)
#         serializer.save(service=service)
#
#         label = '{0} ({1})'.format(service.name, service.organisation.name)
#         send_ga_tracking_event(
#             request._request.path, 'Feedback',
#             'ServiceIncorrectInformationReport', label
#         )
#
#         return Response(serializer.data,
#                         status=status.HTTP_201_CREATED)


# class ServiceRate(APIView):
#     """
#     Rate the quality of a service
#     ---
#     POST:
#          serializer: ServiceRatingSerializer
#     """
#     def post(self, request, *args, **kwargs):
#         service_id = int(kwargs.pop('pk'))
#
#         try:
#             service = Service.objects.get(id=service_id)
#         except Service.DoesNotExist:
#             raise Http404
#
#         serializer = ServiceRatingSerializer(
#             data=request.data
#         )
#
#         serializer.is_valid(raise_exception=True)
#         serializer.save(service=service)
#
#         label = '{0} ({1})'.format(service.name, service.organisation.name)
#         send_ga_tracking_event(
#             request._request.path, 'Feedback',
#             'ServiceRating', label
#         )
#
#         return Response(serializer.data,
#                         status=status.HTTP_201_CREATED)


class ServiceSendSMS(APIView):
    """
    Send an SMS to a supplied cell_number with a supplied service_url
    ---
    POST:
         request_serializer: ServiceSendSMSRequestSerializer
         response_serializer: ServiceSendSMSResponseSerializer
    """
    def post(self, request, *args, **kwargs):
        request_serializer = ServiceSendSMSRequestSerializer(data=request.data)

        request_serializer.is_valid(raise_exception=True)

        analytics_label = ''

        try:
            sender = HttpApiSender(
                settings.VUMI_GO_ACCOUNT_KEY,
                settings.VUMI_GO_CONVERSATION_KEY,
                settings.VUMI_GO_API_TOKEN,
                api_url=settings.VUMI_GO_API_URL
            )

            if 'your_name' in request_serializer.validated_data:
                message = '{0} has sent you a link: {1}'.format(
                    request_serializer.validated_data['your_name'],
                    request_serializer.validated_data['service_url']
                )
                analytics_label = 'send'
            else:
                message = 'You have sent yourself a link: {0}'.format(
                    request_serializer.validated_data['service_url']
                )
                analytics_label = 'save'

            sender.send_text(
                request_serializer.validated_data['cell_number'],
                message
            )

            response_serializer = ServiceSendSMSResponseSerializer(
                data={'result': True}
            )
        except:
            logging.error("Failed to send SMS", exc_info=True)
            response_serializer = ServiceSendSMSResponseSerializer(
                data={'result': False}
            )

        send_ga_tracking_event(
            request._request.path,
            'SMS',
            request_serializer.validated_data['service_url'],
            analytics_label
        )

        response_serializer.is_valid(raise_exception=True)

        return Response(response_serializer.data,
                        status=status.HTTP_200_OK)
