# Счета

Счёт это ссылка на оплату, которую можно отправить покупателю в мессенджере
или по почте. Платёж создаётся автоматически, когда покупатель переходит по
ссылке и платит.

* [Создание счёта](#создание-счёта)
* [Счёт с корзиной](#счёт-с-корзиной)
* [Информация о счёте](#информация-о-счёте)

## Создание счёта

```python
invoice = kassa.invoices.create({
    "payment_data": {
        "amount": {"value": "10.00", "currency": "RUB"},
        "capture": True,
        "description": "Заказ №137",
        "metadata": {"order_id": "137"},
    },
    "cart": [
        {
            "description": "Товар арт. 12345",
            "price": {"value": "10.00", "currency": "RUB"},
            "quantity": 1,
        },
    ],
    "delivery_method_data": {"type": "self"},
    "expires_at": "2026-09-30T00:00:00.000Z",
    "description": "Счёт по заказу №137",
})

print(invoice.id)
print(invoice.status)   # pending, succeeded, canceled

if invoice.delivery_method:
    print(invoice.delivery_method.get("url"))   # ссылка для покупателя
```

Асинхронно:

```python
invoice = await kassa.invoices.create({
    "payment_data": {
        "amount": {"value": "10.00", "currency": "RUB"},
        "capture": True,
    },
    "cart": [
        {
            "description": "Товар арт. 12345",
            "price": {"value": "10.00", "currency": "RUB"},
            "quantity": 1,
        },
    ],
    "delivery_method_data": {"type": "self"},
})
```

## Счёт с корзиной

Позиций может быть несколько. Сумма платежа должна совпадать с суммой корзины.

```python
invoice = kassa.invoices.create({
    "payment_data": {
        "amount": {"value": "1500.00", "currency": "RUB"},
        "capture": True,
        "description": "Заказ №137",
        "receipt": {
            "customer": {"email": "email@email.ru"},
            "items": [
                {
                    "description": "Товар арт. 12345",
                    "quantity": "2.00",
                    "amount": {"value": "500.00", "currency": "RUB"},
                    "vat_code": "2",
                    "payment_mode": "full_payment",
                    "payment_subject": "commodity",
                },
                {
                    "description": "Товар арт. 67890",
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
            "description": "Товар арт. 12345",
            "price": {"value": "500.00", "currency": "RUB"},
            "quantity": 2,
        },
        {
            "description": "Товар арт. 67890",
            "price": {"value": "500.00", "currency": "RUB"},
            "quantity": 1,
        },
    ],
    "delivery_method_data": {"type": "self"},
})
```

## Информация о счёте

```python
invoice = kassa.invoices.get("in-285e5ee7-0022-5000-8000-01516a44b147")

invoice.status
invoice.created_at
invoice.expires_at
invoice.cart
invoice.payment_details    # идентификатор созданного платежа

if invoice.status == "canceled":
    print(invoice.cancellation_details.reason)
```

Когда счёт оплачен, в `payment_details` появляется идентификатор платежа, и
дальше с ним работают как с обычным платежом:

```python
if invoice.payment_details:
    payment = kassa.payments.get(invoice.payment_details["id"])
    print(payment.status)
```
