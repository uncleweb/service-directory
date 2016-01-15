import datetime
from haystack import indexes, models
from models import Service

class ServiceIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)

    # location = indexes.LocationField(model_attr='organisation.location')

    def get_model(self):
        return Service
