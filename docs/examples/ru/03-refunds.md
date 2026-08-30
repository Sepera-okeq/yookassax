# Возвраты

Вернуть можно только успешный платёж и только ту сумму, которая ещё не
возвращена.

* [Создание возврата](#создание-возврата)
* [Частичный возврат](#частичный-возврат)
* [Возврат с чеком](#возврат-с-чеком)
* [Возврат в маркетплейсе](#возврат-в-маркетплейсе)
* [Информация о возврате](#информация-о-возврате)
* [Список возвратов](#список-возвратов)

## Создание возврата

```python
refund = kassa.refunds.create({
    "payment_id": "24e89cb0-000f-5000-9000-1de77fa0d6df",
    "amount": {"value": "9000.00", "currency": "RUB"},
    "description": "Не подошел размер",
})

print(refund.id)
print(refund.status)        # succeeded или canceled
print(refund.is_succeeded)
```

Асинхронно:

```python
refund = await kassa.refunds.create({
    "payment_id": "24e89cb0-000f-5000-9000-1de77fa0d6df",
    "amount": {"value": "9000.00", "currency": "RUB"},
})
```

## Частичный возврат

Сумма возврата меньше суммы платежа. Остаток можно вернуть позже отдельными
возвратами.

```python
payment = kassa.payments.get("24e89cb0-000f-5000-9000-1de77fa0d6df")

# Сколько ещё можно вернуть.
already_refunded = payment.refunded_amount.value if payment.refunded_amount else 0
available = payment.amount.value - already_refunded

refund = kassa.refunds.create({
    "payment_id": payment.id,
    "amount": {"value": "500.00", "currency": "RUB"},
    "description": "Возврат одной позиции",
})
```

Суммы приходят как `Decimal`, поэтому вычитание точное. Приводить их к `float`
не нужно и вредно.

## Возврат с чеком

```python
refund = kassa.refunds.create({
    "payment_id": "24e89cb0-000f-5000-9000-1de77fa0d6df",
    "amount": {"value": "9000.00", "currency": "RUB"},
    "description": "Не подошел размер",
    "receipt": {
        "customer": {
            "full_name": "Иванов Иван Иванович",
            "email": "email@email.ru",
            "phone": "79211234567",
        },
        "items": [
            {
                "description": "Переносное зарядное устройство",
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

## Возврат в маркетплейсе

Когда платёж был распределён между продавцами, в возврате указывают, с чьего
счёта возвращать.

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

## Информация о возврате

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

## Список возвратов

```python
page = kassa.refunds.list(
    payment_id="24e89cb0-000f-5000-9000-1de77fa0d6df",
    limit=20,
)

for refund in page:
    print(refund.id, refund.amount.value, refund.status)
```

Все возвраты по платежу:

```python
for refund in kassa.refunds.iterate(payment_id="24e89cb0-000f-5000-9000-1de77fa0d6df"):
    print(refund.id)
```

Асинхронно:

```python
async for refund in kassa.refunds.iterate(payment_id="24e89cb0-000f-5000-9000-1de77fa0d6df"):
    print(refund.id)
```
