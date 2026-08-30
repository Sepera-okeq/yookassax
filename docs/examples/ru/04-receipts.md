# Чеки

Чек по 54-ФЗ можно пробить отдельно от платежа: например, при постоплате или
когда предмет расчёта известен позже.

* [Чек прихода](#чек-прихода)
* [Чек возврата прихода](#чек-возврата-прихода)
* [Чек с маркированным товаром](#чек-с-маркированным-товаром)
* [Информация о чеке](#информация-о-чеке)
* [Список чеков](#список-чеков)

## Чек прихода

```python
receipt = kassa.receipts.create({
    "type": "payment",
    "payment_id": "24e89cb0-000f-5000-9000-1de77fa0d6df",
    "send": True,
    "customer": {
        "full_name": "Иванов Иван Иванович",
        "email": "email@email.ru",
        "phone": "79211234567",
        "inn": "6321341814",
    },
    "items": [
        {
            "description": "Переносное зарядное устройство",
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

Асинхронно:

```python
receipt = await kassa.receipts.create({...})
```

## Чек возврата прихода

```python
receipt = kassa.receipts.create({
    "type": "refund",
    "refund_id": "216749f7-0016-50be-b000-078d43a63ae4",
    "send": True,
    "customer": {"email": "email@email.ru"},
    "items": [
        {
            "description": "Переносное зарядное устройство",
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

## Чек с маркированным товаром

```python
receipt = kassa.receipts.create({
    "type": "payment",
    "payment_id": "24e89cb0-000f-5000-9000-1de77fa0d6df",
    "send": True,
    "customer": {"email": "email@email.ru"},
    "items": [
        {
            "description": "Сигареты",
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

## Информация о чеке

```python
receipt = kassa.receipts.get("rt-2da5c87d-0384-50e8-a7f3-8de646dd9ec9")

receipt.status                    # pending, succeeded, canceled
receipt.type                      # payment или refund
receipt.fiscal_document_number    # номер фискального документа
receipt.fiscal_storage_number     # номер фискального накопителя
receipt.fiscal_attribute          # фискальный признак
receipt.registered_at             # datetime регистрации в налоговой

for item in receipt.items or []:
    print(item.description, item.quantity, item.amount.value)
```

## Список чеков

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
