from django import forms
from advertising.model import ShareAdvertisingCampaign

class ShareAdvertisingStatsForm(forms.ModelForm):
	 class Meta:
        model = ShareAdvertisingCampaign
