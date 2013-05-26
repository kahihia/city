from django import forms
from advertising.models import AdvertisingCampaign, AdvertisingType
from cities.models import Region


class AdvertisingSetupForm(forms.ModelForm):
    regions = forms.ModelMultipleChoiceField(
        widget=forms.CheckboxSelectMultiple,
        queryset=Region.objects.filter(country__code="CA"),
        required=False
    )

    types = forms.ModelMultipleChoiceField(
        widget=forms.CheckboxSelectMultiple,
        queryset=AdvertisingType.objects.filter(active=True),
        required=False
    )

    class Meta:
        model = AdvertisingCampaign
        fields = (
            'name',
            'regions',
            'all_of_canada',
            'budget'
        )

    def __init__(self, *args, **kwargs):
        super(AdvertisingSetupForm, self).__init__(*args, **kwargs)

        self.fields['name'].error_messages['required'] = 'Campaign name is required'

    def clean(self):
        cleaned_data = self.cleaned_data

        all_of_canada = cleaned_data["all_of_canada"]

        regions = cleaned_data["regions"]

        if not all_of_canada and not regions:
            raise forms.ValidationError("You should choose at least one region")

        if not self.data["types"]:
            raise forms.ValidationError("You should create at least one advertising type")

        return cleaned_data
