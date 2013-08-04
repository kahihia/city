from mamona.utils import get_backend_settings

from . import forms

def get_confirmation_form(payment, order_class):
	paypal = get_backend_settings('paypal')
	form = forms.PaypalConfirmationForm(payment=payment, order_class=order_class)
	return {'form': form, 'method': 'post', 'action': paypal['url']}
