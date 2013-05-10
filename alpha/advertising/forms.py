from django import forms
from advertising.models import AdvertisingCampaign


class AdvertisingSetupForm(forms.ModelForm):
    class Meta:
        model = AdvertisingCampaign
        fields = (
            'name',
        )
