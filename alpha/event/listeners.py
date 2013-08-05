from mamona import signals

from django.core.urlresolvers import reverse
from django.contrib.sites.models import Site

def order_to_payment_listener(sender, order=None, payment=None, **kwargs):
    if order.__class__.__name__ == "FeaturedEventOrder":
        payment.order = order
        payment.amount = order.total_price.amount
        payment.currency = order.cost.currency

def payment_status_changed_listener(sender, instance=None, old_status=None, new_status=None, **kwargs):
    if instance.order.__class__.__name__ == "FeaturedEventOrder":
        if new_status == 'paid':
            instance.order.status = 's'

            featured_event = instance.order.featured_event
            featured_event.active = True
            featured_event.save()

            instance.order.save()
        elif new_status == 'failed':
            instance.order.status = 'f'
            instance.order.save()
        elif new_status == 'partially_paid':
            instance.order.status = 'p'
            instance.order.save()

def return_urls_query_listener(sender, instance=None, urls=None, **kwargs):
    if instance.order.__class__.__name__ == "FeaturedEventOrder":
        url = 'http://%s%s' % (
                Site.objects.get_current().domain,
                reverse('featured_event_order', kwargs={'order_id': instance.order.id})
                )
        urls.update({'paid': url, 'failure': url})

signals.order_to_payment_query.connect(order_to_payment_listener)
signals.payment_status_changed.connect(payment_status_changed_listener)
signals.return_urls_query.connect(return_urls_query_listener)