# Payment methods

A saved payment method lets you charge money again without the payer being
present: subscriptions, recurring payments, one-click checkout.

* [Saving a payment method](#saving-a-payment-method)
* [Saving during the first payment](#saving-during-the-first-payment)
* [Payment method details](#payment-method-details)
* [Charging a saved method](#charging-a-saved-method)

Recurring payments must be enabled for the shop. Otherwise YooKassa answers 403
both when saving and when charging.

## Saving a payment method

A separate flow: the payer links a card without paying anything at that moment.

```python
method = kassa.payment_methods.create({
    "type": "bank_card",
    "client_ip": "1.2.3.4",
    "holder": {"gateway_id": "100700"},
    "confirmation": {
        "type": "redirect",
        "return_url": "https://merchant-site.com/return_url",
    },
    "metadata": {"order_id": "order-72"},
})

print(method.id)
print(method.status)   # pending, active, inactive
print(method.saved)
```

Asynchronously:

```python
method = await kassa.payment_methods.create({
    "type": "bank_card",
    "client_ip": "1.2.3.4",
    "holder": {"gateway_id": "100700"},
    "confirmation": {
        "type": "redirect",
        "return_url": "https://merchant-site.com/return_url",
    },
})
```

## Saving during the first payment

More often the method is saved along the way, together with a regular payment.

```python
payment = kassa.payments.create({
    "amount": {"value": "1000.00", "currency": "RUB"},
    "confirmation": {
        "type": "redirect",
        "return_url": "https://merchant-site.com/return_url",
    },
    "capture": True,
    "save_payment_method": True,
    "description": "First subscription payment",
})
```

After a successful payment the saved method identifier is on the payment:

```python
payment = kassa.payments.get(payment.id)

if payment.is_succeeded and payment.payment_method and payment.payment_method.saved:
    saved_method_id = payment.payment_method.id
    # Store it on your side, you will need it for the next charges.
```

## Payment method details

```python
method = kassa.payment_methods.get("1da5c87d-0984-50e8-a7f3-8de646dd9ec9")

method.type      # bank_card, sbp, yoo_money
method.status
method.saved
method.title     # for example "Bank card *4444"
method.card      # masked number, expiry, issuer
```

## Charging a saved method

```python
payment = kassa.payments.create({
    "amount": {"value": "1000.00", "currency": "RUB"},
    "payment_method_id": saved_method_id,
    "capture": True,
    "description": "Subscription renewal for September",
}, idempotency_key=f"subscription-{subscription_id}-2026-09")
```

No `confirmation` is needed: the payer takes no part in the charge and there is
no redirect.

The idempotency key matters especially here. Subscription charges are triggered
by a scheduler, and a scheduler may repeat a job after a failure. A key built
from the subscription identifier and the period prevents charging twice for the
same month.

Handling a refusal:

```python
from yookassax import Forbidden

try:
    payment = kassa.payments.create({...})
except Forbidden as error:
    # Recurring payments are not enabled for the shop.
    # The error is permanent, retrying the charge is pointless.
    print(error.description)
```
