import logging

from UniversalAnalytics import Tracker
from django.conf import settings
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import D
from django.db.models.query import Prefetch
from django.http import Http404
from go_http import HttpApiSender
from rest_framework import status
from rest_framework.generics import RetrieveAPIView, ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from haystack.query import ValuesListSearchQuerySet
from service_directory.api.haystack_elasticsearch_raw_query.\
    custom_elasticsearch import ConfigurableSearchQuerySet
from service_directory.api.models import Keyword, Category, Organisation
from service_directory.api.serializers import\
    HomePageCategoryKeywordGroupingSerializer, \
    KeywordSerializer, OrganisationSummarySerializer, \
    OrganisationSerializer, OrganisationIncorrectInformationReportSerializer, \
    OrganisationRatingSerializer, OrganisationSendSMSRequestSerializer, \
    OrganisationSendSMSResponseSerializer

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
            - name: radius
              description: limit response to user location within this radius
              type: int
              default: 25 (KMs)
        response_serializer: OrganisationSummarySerializer
    """
    def get(self, request):
        point = None
        radius = None
        search_term = ''
        place_name = None
        country = request.query_params.get('country')
        categories = request.query_params.get('categories', [])

        if 'radius' in request.query_params:
            radius = int(request.query_params['radius'].strip())

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

        if categories:
            sqs = sqs.filter(categories=categories)

        if country:
            sqs = sqs.filter(country=country)

        if point:
            sqs = sqs.distance('location', point).order_by('distance')

            if radius:
                sqs = sqs.dwithin('location', point, D(km=radius))

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
            if distance is not None and distance.m != float("inf"):
                organisation.distance = '{0:.2f}km'.format(distance.km)

        if organisation_distance_tuples:
            services = zip(*organisation_distance_tuples)[0]
            serializer = OrganisationSummarySerializer(services, many=True)
            return Response(serializer.data)

        return Response([])


class OrganisationDetail(RetrieveAPIView):
    """
    Retrieve organisation details
    """
    queryset = Organisation.objects.all()
    serializer_class = OrganisationSerializer

    def get(self, request, *args, **kwargs):
        response = super(OrganisationDetail, self).get(
            request, *args, **kwargs
        )

        if response and response.data:
            try:
                organisation_name = response.data['name']
                send_ga_tracking_event(
                    request._request.path,
                    'View',
                    'Organisation',
                    organisation_name
                )
            except (KeyError, TypeError):
                logging.warn("Did not find expected data in response to make"
                             " Google Analytics call", exc_info=True)

        return response


class OrganisationReportIncorrectInformation(APIView):
    """
    Report incorrect information for an organisation
    ---
    POST:
         serializer: OrganisationIncorrectInformationReportSerializer
    """
    def post(self, request, *args, **kwargs):
        organisation_id = int(kwargs.pop('pk'))

        try:
            organisation = Organisation.objects.get(id=organisation_id)
        except Organisation.DoesNotExist:
            raise Http404

        serializer = OrganisationIncorrectInformationReportSerializer(
            data=request.data
        )

        serializer.is_valid(raise_exception=True)
        serializer.save(organisation=organisation)

        send_ga_tracking_event(
            request._request.path,
            'Feedback',
            'OrganisationIncorrectInformationReport',
            organisation.name
        )

        return Response(serializer.data,
                        status=status.HTTP_201_CREATED)


class OrganisationRate(APIView):
    """
    Rate the quality of an organisation
    ---
    POST:
         serializer: OrganisationRatingSerializer
    """
    def post(self, request, *args, **kwargs):
        organisation_id = int(kwargs.pop('pk'))

        try:
            organisation = Organisation.objects.get(id=organisation_id)
        except Organisation.DoesNotExist:
            raise Http404

        serializer = OrganisationRatingSerializer(
            data=request.data
        )

        serializer.is_valid(raise_exception=True)
        serializer.save(organisation=organisation)

        send_ga_tracking_event(
            request._request.path,
            'Feedback',
            'OrganisationRating',
            organisation.name
        )

        return Response(serializer.data,
                        status=status.HTTP_201_CREATED)


class OrganisationSendSMS(APIView):
    """
    Send an SMS to a supplied cell_number with a supplied organisation_url
    ---
    POST:
         request_serializer: OrganisationSendSMSRequestSerializer
         response_serializer: OrganisationSendSMSResponseSerializer
    """
    def post(self, request, *args, **kwargs):
        request_serializer = OrganisationSendSMSRequestSerializer(
            data=request.data
        )

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
                    request_serializer.validated_data['organisation_url']
                )
                analytics_label = 'send'
            else:
                message = 'You have sent yourself a link: {0}'.format(
                    request_serializer.validated_data['organisation_url']
                )
                analytics_label = 'save'

            sender.send_text(
                request_serializer.validated_data['cell_number'],
                message
            )

            response_serializer = OrganisationSendSMSResponseSerializer(
                data={'result': True}
            )
        except:
            logging.error("Failed to send SMS", exc_info=True)
            response_serializer = OrganisationSendSMSResponseSerializer(
                data={'result': False}
            )

        send_ga_tracking_event(
            request._request.path,
            'SMS',
            request_serializer.validated_data['organisation_url'],
            analytics_label
        )

        response_serializer.is_valid(raise_exception=True)

        return Response(response_serializer.data,
                        status=status.HTTP_200_OK)
