# Invoices

An invoice is a payment link you can send to a buyer over a messenger or by
email. The payment is created automatically once the buyer follows the link and
pays.

* [Creating an invoice](#creating-an-invoice)
* [Invoice with a cart](#invoice-with-a-cart)
* [Invoice details](#invoice-details)

## Creating an invoice

```python
invoice = kassa.invoices.create({
    "payment_data": {
        "amount": {"value": "10.00", "currency": "RUB"},
        "capture": True,
        "description": "Order 137",
        "metadata": {"order_id": "137"},
    },
    "cart": [
        {
            "description": "Item 12345",
            "price": {"value": "10.00", "currency": "RUB"},
            "quantity": 1,
        },
    ],
    "delivery_method_data": {"type": "self"},
    "expires_at": "2026-09-30T00:00:00.000Z",
    "description": "Invoice for order 137",
})

print(invoice.id)
print(invoice.status)   # pending, succeeded, canceled

if invoice.delivery_method:
    print(invoice.delivery_method.get("url"))   # the link for the buyer
```

Asynchronously:

```python
invoice = await kassa.invoices.create({
    "payment_data": {
        "amount": {"value": "10.00", "currency": "RUB"},
        "capture": True,
    },
    "cart": [
        {
            "description": "Item 12345",
            "price": {"value": "10.00", "currency": "RUB"},
            "quantity": 1,
        },
    ],
    "delivery_method_data": {"type": "self"},
})
```

## Invoice with a cart

There may be several items. The payment amount must match the cart total.

```python
invoice = kassa.invoices.create({
    "payment_data": {
        "amount": {"value": "1500.00", "currency": "RUB"},
        "capture": True,
        "description": "Order 137",
        "receipt": {
            "customer": {"email": "email@email.com"},
            "items": [
                {
                    "description": "Item 12345",
                    "quantity": "2.00",
                    "amount": {"value": "500.00", "currency": "RUB"},
                    "vat_code": "2",
                    "payment_mode": "full_payment",
                    "payment_subject": "commodity",
                },
                {
                    "description": "Item 67890",
                    "quantity": "1.00",
                    "amount": {"value": "500.00", "currency": "RUB"},
                    "vat_code": "2",
                    "payment_mode": "full_payment",
                    "payment_subject": "commodity",
                },
            ],
        },
    },
    "cart": [
        {
            "description": "Item 12345",
            "price": {"value": "500.00", "currency": "RUB"},
            "quantity": 2,
        },
        {
            "description": "Item 67890",
            "price": {"value": "500.00", "currency": "RUB"},
            "quantity": 1,
        },
    ],
    "delivery_method_data": {"type": "self"},
})
```

## Invoice details

```python
invoice = kassa.invoices.get("in-285e5ee7-0022-5000-8000-01516a44b147")

invoice.status
invoice.created_at
invoice.expires_at
invoice.cart
invoice.payment_details    # identifier of the created payment

if invoice.status == "canceled":
    print(invoice.cancellation_details.reason)
```

Once the invoice is paid, `payment_details` carries the payment identifier, and
from there you work with it as with any payment:

```python
if invoice.payment_details:
    payment = kassa.payments.get(invoice.payment_details["id"])
    print(payment.status)
```
