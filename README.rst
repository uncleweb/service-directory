service-directory
=============================

A service directory of information.

Prerequisites:

* PostgreSQL with the following extensions:
  - postgis [CREATE EXTENSION postgis;]
    OSMGeoAdmin for the Organisation model, ordering by distance in haystack.
  - citext  [CREATE EXTENSION citext;]
    Case-insensitive text columns for things like category & keyword name.


The following keys should be set in the django projects settings file (the values are only examples):

GOOGLE_ANALYTICS_TRACKING_ID = 'UA-VALIDKEY'

ideally things like the passwords and api keys should be kept out of the repository and possibly included in the
settings through importing from a secrets file that is ignored by the version control.

eg in settings.py:

try:
    from secrets import *
except ImportError:
    raise

.. image:: https://travis-ci.org/praekelt/service-directory.svg?branch=develop
        :target: https://travis-ci.org/praekelt/service-directory

.. image:: https://coveralls.io/repos/praekelt/service-directory/badge.svg?branch=develop&service=github
    :target: https://coveralls.io/github/praekelt/service-directory?branch=develop
    :alt: Code Coverage

.. image:: https://readthedocs.org/projects/service-directory/badge/?version=latest
    :target: https://service-directory.readthedocs.org/en/latest/
    :alt: Service Directory Docs
