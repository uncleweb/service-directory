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
        'ENGINE': 'haystack.backends.elasticsearch_backend.ElasticsearchSearchEngine',
        'URL': 'http://%s:9200' % environ.get('ES_HOST', '127.0.0.1'),
        'INDEX_NAME': 'haystack',
    },
}
