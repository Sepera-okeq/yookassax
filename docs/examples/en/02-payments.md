# Payments

A payment is the central object of the API. It has a linear lifecycle and moves
from one status to the next.

* [Creating a payment](#creating-a-payment)
* [Payment with a receipt](#payment-with-a-receipt)
* [Two-stage payment](#two-stage-payment)
* [Partial capture](#partial-capture)
* [Cancelling a payment](#cancelling-a-payment)
* [Payment details](#payment-details)
* [Listing payments with filters](#listing-payments-with-filters)
* [Charging a saved payment method](#charging-a-saved-payment-method)
* [Utility bill payment](#utility-bill-payment)

## Creating a payment

```python
payment = kassa.payments.create({
    "amount": {"value": "1000.00", "currency": "RUB"},
    "confirmation": {
        "type": "redirect",
        "return_url": "https://merchant-site.com/return_url",
    },
    "capture": True,
    "description": "Order 72",
    "metadata": {"order_number": "72"},
})

print(payment.id)
print(payment.status)             # pending
print(payment.confirmation_url)   # send the payer here
```

Asynchronously:

```python
payment = await kassa.payments.create({
    "amount": {"value": "1000.00", "currency": "RUB"},
    "confirmation": {
        "type": "redirect",
        "return_url": "https://merchant-site.com/return_url",
    },
    "capture": True,
    "description": "Order 72",
})
```

Pass the amount as a string, not as a floating point number: `"1000.00"`, not
`1000.0`. In the response it comes back as a `Decimal`.

The idempotency key is added automatically. Supplying your own makes sense when
your code may retry the call:

```python
payment = kassa.payments.create(params, idempotency_key=f"order-{order_id}")
```

A second call with the same key returns the existing payment instead of
creating another one.

## Payment with a receipt

A receipt is produced together with the payment if the shop is subject to
Russian fiscalization law.

```python
payment = kassa.payments.create({
    "amount": {"value": "1000.00", "currency": "RUB"},
    "confirmation": {
        "type": "redirect",
        "return_url": "https://merchant-site.com/return_url",
    },
    "capture": True,
    "description": "Order 72",
    "receipt": {
        "customer": {
            "full_name": "Ivanov Ivan Ivanovich",
            "email": "email@email.com",
            "phone": "79211234567",
            "inn": "6321341814",
        },
        "items": [
            {
                "description": "Portable power bank",
                "quantity": "1.00",
                "amount": {"value": "1000.00", "currency": "RUB"},
                "vat_code": "2",
                "payment_mode": "full_payment",
                "payment_subject": "commodity",
                "country_of_origin_code": "CN",
            },
        ],
    },
})
```

## Two-stage payment

With `capture=False` the money is held on the payer's card but not debited. You
must capture or cancel within the allowed time, otherwise the payment cancels
itself and the money goes back.

```python
payment = kassa.payments.create({
    "amount": {"value": "1000.00", "currency": "RUB"},
    "confirmation": {
        "type": "redirect",
        "return_url": "https://merchant-site.com/return_url",
    },
    "capture": False,
    "description": "Order 72",
})

# Later, once the goods are ready to ship.
if payment.is_waiting_for_capture:
    payment = kassa.payments.capture(payment.id)
    print(payment.status)   # succeeded
```

Asynchronously:

```python
payment = await kassa.payments.capture(payment.id)
```

## Partial capture

You may capture less than the original amount. The remainder returns to the
payer.

```python
payment = kassa.payments.capture(
    "21b23b5b-000f-5061-a000-0674e49a8c10",
    {"amount": {"value": "800.00", "currency": "RUB"}},
)
```

Splitting between marketplace sellers:

```python
payment = kassa.payments.capture(
    "21b23b5b-000f-5061-a000-0674e49a8c10",
    {
        "amount": {"value": "1000.00", "currency": "RUB"},
        "transfers": [
            {"account_id": "123", "amount": {"value": "300.00", "currency": "RUB"}},
            {"account_id": "456", "amount": {"value": "700.00", "currency": "RUB"}},
        ],
    },
)
```

## Cancelling a payment

Only a payment in the `waiting_for_capture` status can be cancelled. For cards
and the YooMoney wallet the money returns instantly; other methods may take
several days.

```python
payment = kassa.payments.cancel("21b23b5b-000f-5061-a000-0674e49a8c10")
print(payment.status)   # canceled
```

```python
payment = await kassa.payments.cancel("21b23b5b-000f-5061-a000-0674e49a8c10")
```

## Payment details

```python
payment = kassa.payments.get("21b23b5b-000f-5061-a000-0674e49a8c10")

payment.status                  # pending, waiting_for_capture, succeeded, canceled
payment.amount.value            # Decimal("1000.00")
payment.amount.currency         # "RUB"
payment.created_at              # timezone aware datetime
payment.paid                    # bool
payment.refundable              # whether a refund is possible
payment.metadata                # the dictionary you passed on creation

payment.is_pending
payment.is_waiting_for_capture
payment.is_succeeded
payment.is_canceled
```

If a payment was cancelled, the reason sits in `cancellation_details`:

```python
if payment.is_canceled:
    print(payment.cancellation_details.party)    # who cancelled
    print(payment.cancellation_details.reason)   # why
```

A field the model does not know about yet is available through:

```python
payment.extra("new_api_field")
```

The library warns about such a field once: YooKassa has extended the response
and `yookassax` is worth updating. Details in the
[errors guide](14-errors.md#fields-the-model-does-not-know).

## Listing payments with filters

One page at a time:

```python
page = kassa.payments.list(
    status="succeeded",
    limit=50,
    created_at_gte="2026-08-01T00:00:00.000Z",
    created_at_lt="2026-09-01T00:00:00.000Z",
)

for payment in page:
    print(payment.id, payment.amount.value)

print(page.next_cursor)
print(page.has_more)
```

The next page:

```python
next_page = kassa.payments.list(status="succeeded", cursor=page.next_cursor)
```

Everything at once, without handling cursors:

```python
for payment in kassa.payments.iterate(status="succeeded"):
    print(payment.id)
```

Asynchronously:

```python
async for payment in kassa.payments.iterate(status="succeeded"):
    print(payment.id)
```

Filters match the API documentation. Dots in parameter names become
underscores: `created_at.gte` turns into `created_at_gte`.

## Charging a saved payment method

A charge without the payer being present. The method must be saved in advance,
see the [payment methods guide](11-payment-methods.md).

```python
payment = kassa.payments.create({
    "amount": {"value": "1000.00", "currency": "RUB"},
    "payment_method_id": "1da5c87d-0984-50e8-a7f3-8de646dd9ec9",
    "capture": True,
    "description": "Subscription renewal",
})
```

No `confirmation` is needed here: there is no redirect, and
`confirmation_url` comes back empty.

If recurring payments are not enabled for the shop, YooKassa answers 403:

```python
from yookassax import Forbidden

try:
    payment = kassa.payments.create({...})
except Forbidden as error:
    print("Recurring payments are not enabled:", error.description)
```

## Utility bill payment

```python
payment = kassa.payments.create({
    "amount": {"value": "100.00", "currency": "RUB"},
    "confirmation": {
        "type": "redirect",
        "return_url": "https://merchant-site.com/return_url",
    },
    "capture": True,
    "payment_order": {
        "type": "utilities",
        "amount": {"value": "100.00", "currency": "RUB"},
        "payment_purpose": "Utility bill for July 2026",
        "recipient": {
            "name": "Zhilfond Management Company",
            "inn": "6321341814",
            "kpp": "987654321",
            "bank": {
                "name": "Sberbank",
                "bic": "044525225",
                "account": "40702810000000000001",
                "correspondent_account": "30101810400000000225",
            },
        },
        "kbk": "18210102000011000110",
        "oktmo": "45382000",
        "payment_period": {"month": 7, "year": 2026},
        "account_number": "1234567890",
    },
})
```
