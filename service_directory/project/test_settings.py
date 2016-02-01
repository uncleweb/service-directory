from settings import *


# we need a user that is a superuser because we need to be able to run
# CREATE EXTENSION commands
# CREATEDB permission is also required
DATABASES['default']['USER'] = 'postgres'
DATABASES['default']['PASSWORD'] = 'password'

HAYSTACK_CONNECTIONS['default']['INDEX_NAME'] = 'test'

# turn off authentication on the api for testing
REST_FRAMEWORK['DEFAULT_PERMISSION_CLASSES'] = ('rest_framework.permissions.AllowAny',)
