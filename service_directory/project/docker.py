from os import environ

import dj_database_url

from .settings import *


# Disable debug mode

DEBUG = False
TEMPLATE_DEBUG = False

ALLOWED_HOSTS = ['*']

SECRET_KEY = environ.get('SECRET_KEY', 'please-change-me')

RAVEN_DSN = environ.get('RAVEN_DSN')
RAVEN_CONFIG = {'dsn': RAVEN_DSN} if RAVEN_DSN else {}

STATIC_ROOT = '/deploy/static'

DATABASES = {
    'default': dj_database_url.config()
}

HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'service_directory.api.haystack_elasticsearch_raw_query.custom_elasticsearch.ConfigurableElasticSearchEngine',
        'URL': 'http://%s:9200' % environ.get('ES_HOST', '127.0.0.1'),
        'INDEX_NAME': environ.get('HAYSTACK_INDEX_NAME', 'haystack'),
    },
}

GOOGLE_ANALYTICS_TRACKING_ID = environ.get('GOOGLE_ANALYTICS_TRACKING_ID', 'please-change-me')

VUMI_GO_ACCOUNT_KEY = environ.get('VUMI_GO_ACCOUNT_KEY', 'please-change-me')
VUMI_GO_CONVERSATION_KEY = environ.get('VUMI_GO_CONVERSATION_KEY', 'please-change-me')
VUMI_GO_API_TOKEN = environ.get('VUMI_GO_API_TOKEN', 'please-change-me')
VUMI_GO_API_URL = environ.get('VUMI_GO_API_URL', 'please-change-me')