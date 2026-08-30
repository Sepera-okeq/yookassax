# Receipts

A receipt can be issued separately from the payment: for post-payment scenarios
or when the subject of settlement becomes known later.

* [Sale receipt](#sale-receipt)
* [Refund receipt](#refund-receipt)
* [Receipt with a marked product](#receipt-with-a-marked-product)
* [Receipt details](#receipt-details)
* [Listing receipts](#listing-receipts)

## Sale receipt

```python
receipt = kassa.receipts.create({
    "type": "payment",
    "payment_id": "24e89cb0-000f-5000-9000-1de77fa0d6df",
    "send": True,
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
        },
    ],
    "settlements": [
        {
            "type": "cashless",
            "amount": {"value": "1000.00", "currency": "RUB"},
        },
    ],
})

print(receipt.id)
print(receipt.status)
```

Asynchronously:

```python
receipt = await kassa.receipts.create({...})
```

## Refund receipt

```python
receipt = kassa.receipts.create({
    "type": "refund",
    "refund_id": "216749f7-0016-50be-b000-078d43a63ae4",
    "send": True,
    "customer": {"email": "email@email.com"},
    "items": [
        {
            "description": "Portable power bank",
            "quantity": "1.00",
            "amount": {"value": "1000.00", "currency": "RUB"},
            "vat_code": "2",
            "payment_mode": "full_payment",
            "payment_subject": "commodity",
        },
    ],
    "settlements": [
        {
            "type": "cashless",
            "amount": {"value": "1000.00", "currency": "RUB"},
        },
    ],
})
```

## Receipt with a marked product

```python
receipt = kassa.receipts.create({
    "type": "payment",
    "payment_id": "24e89cb0-000f-5000-9000-1de77fa0d6df",
    "send": True,
    "customer": {"email": "email@email.com"},
    "items": [
        {
            "description": "Cigarettes",
            "quantity": "1.00",
            "amount": {"value": "200.00", "currency": "RUB"},
            "vat_code": "1",
            "payment_mode": "full_payment",
            "payment_subject": "commodity",
            "measure": "piece",
            "mark_mode": "0",
            "mark_code_info": {
                "gs_1m": "010460406000600021N4N57RTCBUZTQ2403054002054103104",
            },
            "mark_quantity": {"numerator": 1, "denominator": 1},
        },
    ],
    "settlements": [
        {"type": "cashless", "amount": {"value": "200.00", "currency": "RUB"}},
    ],
})
```

## Receipt details

```python
receipt = kassa.receipts.get("rt-2da5c87d-0384-50e8-a7f3-8de646dd9ec9")

receipt.status                    # pending, succeeded, canceled
receipt.type                      # payment or refund
receipt.fiscal_document_number
receipt.fiscal_storage_number
receipt.fiscal_attribute
receipt.registered_at             # datetime of tax registration

for item in receipt.items or []:
    print(item.description, item.quantity, item.amount.value)
```

## Listing receipts

```python
page = kassa.receipts.list(
    payment_id="24e89cb0-000f-5000-9000-1de77fa0d6df",
    limit=20,
)

for receipt in page:
    print(receipt.id, receipt.status)
```

```python
for receipt in kassa.receipts.iterate(status="succeeded"):
    print(receipt.id)
```
