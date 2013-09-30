from django import forms
from djmoney.forms.fields import MoneyField


class FreeTryForm(forms.Form):
    budget = MoneyField()
