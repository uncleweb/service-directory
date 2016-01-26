import views
from django.conf.urls import url, include


urlpatterns = [
    url(r'^', include('rest_framework_swagger.urls')),

    url(
        r'^homepage_categories_keywords/$',
        views.HomePageCategoryKeywordGrouping.as_view()
    ),

    url(r'^service_lookup/$', views.ServiceLookupView.as_view()),
    url(r'^service/(?P<pk>[0-9]+)/$', views.ServiceDetail.as_view()),

    url(r'^search/', include('haystack.urls')),
]
