from django import forms
from advertising.models import AdvertisingCampaign, AdvertisingType
from cities.models import Region

from django.core.files.images import get_image_dimensions


# class AdvertisingsWidget(forms.Widget):
#     pass


# class ModelAdvertisingsField(forms.MultiValueField):
#     widget = AdvertisingsWidget

#     def __init__(self, advertising_types=AdvertisingType.objects.filter(active=True), *args, **kwargs):
#         super(ModelMultipleChoiceField, self).__init__(required, *args, **kwargs)
#         self.advertising_types = advertising_types

#     def clean(self, value):
#         pass


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

    # advertisings = ModelAdvertisingsField()

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

        if "advertising_types" not in self.data:
            raise forms.ValidationError("You should create at least one advertising type")

        advertising_types = self.data.getlist("advertising_types")

        advertising_payment_types = { int(key.split(".")[1]): value for key, value in self.data.iteritems() if key.startswith("advertising_payment_type") }
        advertising_images = { int(key.split(".")[1]): value for key, value in self.files.iteritems() if key.startswith("advertising_image") }

        advertising_types = AdvertisingType.objects.filter(active=True, id__in=map(lambda s: int(s), advertising_types))

        cleaned_data["advertising_payment_types"] = advertising_payment_types
        cleaned_data["advertising_images"] = advertising_images

        for advertising_type in advertising_types:

            if advertising_type.id not in advertising_images:
                raise forms.ValidationError("You should upload image for all advertising types")

            dimensions = get_image_dimensions(advertising_images[advertising_type.id])

            if dimensions is None:
                raise forms.ValidationError("You can upload only image")

            width, height = dimensions

            if advertising_type.width != width or advertising_type.height != height:
                raise forms.ValidationError("Advertising %s should have %dx%d dimension, you upload image with %dx%d" % (
                        advertising_type.name, advertising_type.width, advertising_type.height, width, height
                    )
                )

        return cleaned_data
