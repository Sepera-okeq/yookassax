# Refunds

Only a successful payment can be refunded, and only up to the amount that has
not been refunded yet.

* [Creating a refund](#creating-a-refund)
* [Partial refund](#partial-refund)
* [Refund with a receipt](#refund-with-a-receipt)
* [Marketplace refund](#marketplace-refund)
* [Refund details](#refund-details)
* [Listing refunds](#listing-refunds)

## Creating a refund

```python
refund = kassa.refunds.create({
    "payment_id": "24e89cb0-000f-5000-9000-1de77fa0d6df",
    "amount": {"value": "9000.00", "currency": "RUB"},
    "description": "Wrong size",
})

print(refund.id)
print(refund.status)        # succeeded or canceled
print(refund.is_succeeded)
```

Asynchronously:

```python
refund = await kassa.refunds.create({
    "payment_id": "24e89cb0-000f-5000-9000-1de77fa0d6df",
    "amount": {"value": "9000.00", "currency": "RUB"},
})
```

## Partial refund

The refund amount is smaller than the payment amount. The remainder can be
refunded later with separate refunds.

```python
payment = kassa.payments.get("24e89cb0-000f-5000-9000-1de77fa0d6df")

# How much is still refundable.
already_refunded = payment.refunded_amount.value if payment.refunded_amount else 0
available = payment.amount.value - already_refunded

refund = kassa.refunds.create({
    "payment_id": payment.id,
    "amount": {"value": "500.00", "currency": "RUB"},
    "description": "Refund for one item",
})
```

Amounts arrive as `Decimal`, so the subtraction is exact. Converting them to
`float` is unnecessary and harmful.

## Refund with a receipt

```python
refund = kassa.refunds.create({
    "payment_id": "24e89cb0-000f-5000-9000-1de77fa0d6df",
    "amount": {"value": "9000.00", "currency": "RUB"},
    "description": "Wrong size",
    "receipt": {
        "customer": {
            "full_name": "Ivanov Ivan Ivanovich",
            "email": "email@email.com",
            "phone": "79211234567",
        },
        "items": [
            {
                "description": "Portable power bank",
                "quantity": "1.00",
                "amount": {"value": "9000.00", "currency": "RUB"},
                "vat_code": "2",
                "payment_mode": "full_payment",
                "payment_subject": "commodity",
            },
        ],
    },
})
```

## Marketplace refund

When the payment was split between sellers, the refund states whose balance the
money comes from.

```python
refund = kassa.refunds.create({
    "payment_id": "24e89cb0-000f-5000-9000-1de77fa0d6df",
    "amount": {"value": "9000.00", "currency": "RUB"},
    "sources": [
        {
            "account_id": "456",
            "amount": {"value": "9000.00", "currency": "RUB"},
        },
    ],
})
```

## Refund details

```python
refund = kassa.refunds.get("216749f7-0016-50be-b000-078d43a63ae4")

refund.payment_id
refund.status
refund.amount.value
refund.created_at

if refund.status == "canceled":
    print(refund.cancellation_details.party)
    print(refund.cancellation_details.reason)
```

## Listing refunds

```python
page = kassa.refunds.list(
    payment_id="24e89cb0-000f-5000-9000-1de77fa0d6df",
    limit=20,
)

for refund in page:
    print(refund.id, refund.amount.value, refund.status)
```

All refunds for a payment:

```python
for refund in kassa.refunds.iterate(payment_id="24e89cb0-000f-5000-9000-1de77fa0d6df"):
    print(refund.id)
```

Asynchronously:

```python
async for refund in kassa.refunds.iterate(payment_id="24e89cb0-000f-5000-9000-1de77fa0d6df"):
    print(refund.id)
```
