import django_filters
from advertising.models import AdvertisingCampaign

class AdvertisingCampaignFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_type='icontains')
    account = django_filters.CharFilter(lookup_type='user__username__icontains')
    class Meta:
        model = AdvertisingCampaign
        fields = ['name', 'account', 'enough_money']
        order_by = (
            ('name', 'Name Asc'),
            ('-name', 'Name Desc'),
        )