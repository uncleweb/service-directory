from settings import *


# we need a user that is a superuser because we need to be able to run
# CREATE EXTENSION postgis;
# CREATEDB permission is also required
DATABASES['default']['USER'] = 'postgres'
DATABASES['default']['PASSWORD'] = 'password'
