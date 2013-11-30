import django_filters
from advertising.models import AdvertisingOrder
from event.models import FeaturedEventOrder

class AdvertisingOrderFilter(django_filters.FilterSet):
    campaign = django_filters.CharFilter(lookup_type='name__icontains')
    class Meta:
        model = AdvertisingOrder
        fields = ['campaign', 'account']
        

class FeaturedEventOrderFilter(django_filters.FilterSet):
    featured_event = django_filters.CharFilter(lookup_type='event__name__icontains')
    class Meta:
        model = FeaturedEventOrder
        fields = ['featured_event', 'account']        