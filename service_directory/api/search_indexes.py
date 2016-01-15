from haystack import indexes
from models import Service


class ServiceIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)

    location = indexes.LocationField(model_attr='organisation__location')

    def get_model(self):
        return Service
