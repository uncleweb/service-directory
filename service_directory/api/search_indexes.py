from haystack import indexes
from models import Organisation


class OrganisationIndex(indexes.SearchIndex, indexes.Indexable):
    categories = indexes.MultiValueField(null=True)

    text = indexes.CharField(document=True, use_template=True)
    location = indexes.LocationField(model_attr='location', null=True)
    country = indexes.CharField(model_attr='country__iso_code', null=True)

    def get_model(self):
        return Organisation

    def prepare_categories(self, obj):
        # Since we're using a M2M relationship with a complex lookup,
        return [
            category.id for category in
            obj.categories.order_by('pk')
        ]
