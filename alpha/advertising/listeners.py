from mamona import signals

def order_to_payment_listener(sender, order=None, payment=None, **kwargs):
    payment.order = order
    payment.amount = order.budget.amount
    payment.currency = order.budget.currency

signals.order_to_payment_query.connect(order_to_payment_listener)