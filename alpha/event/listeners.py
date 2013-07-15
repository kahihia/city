from mamona import signals

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

signals.order_to_payment_query.connect(order_to_payment_listener)
signals.payment_status_changed.connect(payment_status_changed_listener)