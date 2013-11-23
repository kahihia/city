import django_filters
from advertising.models import AdvertisingCampaign

class AdvertisingCampaignFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_type='icontains')
    class Meta:
        model = AdvertisingCampaign
        fields = ['name', 'account', 'enough_money', 'free']
        order_by = (
            ('name', 'Name Asc'),
            ('-name', 'Name Desc'),
        )