import views
from django.conf.urls import url, include


urlpatterns = [
    url(r'^', include('rest_framework_swagger.urls')),

    url(r'^service_lookup/$', views.ServiceLookupView.as_view())
]
