import views
from django.conf.urls import url, include


urlpatterns = [
    url(r'^', include('rest_framework_swagger.urls')),

    url(
        r'^homepage_categories_keywords/$',
        views.HomePageCategoryKeywordGrouping.as_view()
    ),

    url(r'^keywords/$', views.KeywordList.as_view()),

    url(r'^search/$', views.Search.as_view()),
    url(r'^organisation/(?P<pk>[0-9]+)/$', views.OrganisationDetail.as_view()),
    url(r'^organisation/(?P<pk>[0-9]+)/report/$',
        views.OrganisationReportIncorrectInformation.as_view()),
    url(r'^organisation/(?P<pk>[0-9]+)/rate/$',
        views.OrganisationRate.as_view()),
    url(r'^organisation/sms/$',
        views.OrganisationSendSMS.as_view()),

    url(r'^search_form/$', include('haystack.urls')),
]
