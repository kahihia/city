from django import forms
from advertising.models import AdvertisingCampaign, AdvertisingType
from cities.models import Region

from django.core.files.images import get_image_dimensions

from djmoney.forms.fields import MoneyField
from moneyed import Money, CAD


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
            'website'
        )

    def __init__(self, *args, **kwargs):
        super(AdvertisingSetupForm, self).__init__(*args, **kwargs)

        self.fields['name'].error_messages['required'] = 'Campaign name is required'
        self.fields['website'].error_messages['required'] = 'Website URL is required'

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


class AdvertisingCampaignEditForm(AdvertisingSetupForm):
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

            if advertising_type.id in advertising_images:
                dimensions = get_image_dimensions(advertising_images[advertising_type.id])

                if dimensions is None:
                    raise forms.ValidationError("You can upload only image")

                width, height = dimensions

                if advertising_type.width != width or advertising_type.height != height:
                    raise forms.ValidationError("Advertising %s should have %dx%d dimension, you upload image with %dx%d" % (
                            advertising_type.name, advertising_type.width, advertising_type.height, width, height
                        )
                    )

            elif int(advertising_type.id) not in self.instance.advertising_set.values_list("ad_type_id", flat=True):
                raise forms.ValidationError("You should upload image for all advertising types")

        return cleaned_data        



class PaidAdvertisingSetupForm(AdvertisingSetupForm):
    order_budget = MoneyField(min_value=Money(10, CAD))

    def __init__(self, *args, **kwargs):
        super(PaidAdvertisingSetupForm, self).__init__(*args, **kwargs)

        self.fields['order_budget'].error_messages['min_value'] = 'Ensure budget is greater than or equal to %(limit_value)s'


class DepositFundsForCampaignForm(forms.Form):
    order_budget = MoneyField(min_value=Money(10, CAD))

    def __init__(self, *args, **kwargs):
        super(DepositFundsForCampaignForm, self).__init__(*args, **kwargs)
        self.fields['order_budget'].error_messages['min_value'] = 'Ensure budget is greater than or equal to %(limit_value)s'