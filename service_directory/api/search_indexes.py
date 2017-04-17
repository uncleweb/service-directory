from haystack import indexes
from models import Organisation


class OrganisationIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)

    location = indexes.LocationField(model_attr='location', null=True)

    def get_model(self):
        return Organisation
