# Выплаты

Выплата переводит деньги с баланса магазина получателю: на карту, в кошелёк
ЮMoney или через СБП.

* [Выплата на банковскую карту](#выплата-на-банковскую-карту)
* [Выплата через СБП](#выплата-через-сбп)
* [Выплата в кошелёк ЮMoney](#выплата-в-кошелёк-юmoney)
* [Выплата самозанятому](#выплата-самозанятому)
* [Выплата по токену](#выплата-по-токену)
* [Информация о выплате](#информация-о-выплате)
* [Список выплат](#список-выплат)
* [Поиск выплат](#поиск-выплат)

Для выплат нужен отдельный ключ доступа: секретный ключ магазина здесь не
подходит.

## Выплата на банковскую карту

```python
payout = kassa.payouts.create({
    "amount": {"value": "280.00", "currency": "RUB"},
    "payout_destination_data": {
        "type": "bank_card",
        "card": {"number": "5555555555554477"},
    },
    "description": "Выплата по заказу №37",
    "metadata": {"order_id": "37"},
})

print(payout.id)
print(payout.status)   # pending, succeeded, canceled
```

Асинхронно:

```python
payout = await kassa.payouts.create({
    "amount": {"value": "280.00", "currency": "RUB"},
    "payout_destination_data": {
        "type": "bank_card",
        "card": {"number": "5555555555554477"},
    },
})
```

## Выплата через СБП

Получателя определяют по телефону и банку из [справочника
СБП](09-sbp-banks.md). Персональные данные нужно передать заранее, см.
[примеры по персональным данным](08-personal-data.md).

```python
payout = kassa.payouts.create({
    "amount": {"value": "280.00", "currency": "RUB"},
    "payout_destination_data": {
        "type": "sbp",
        "phone": "79001002030",
        "bank_id": "100000000111",
    },
    "personal_data": [
        {"id": "pd-285e5ee7-0022-5000-8000-01516a44b147"},
    ],
    "description": "Выплата по заказу №37",
})
```

## Выплата в кошелёк ЮMoney

```python
payout = kassa.payouts.create({
    "amount": {"value": "280.00", "currency": "RUB"},
    "payout_destination_data": {
        "type": "yoo_money",
        "account_number": "410011758831136",
    },
    "description": "Выплата по заказу №37",
})
```

## Выплата самозанятому

Самозанятого нужно зарегистрировать заранее, см. [примеры по
самозанятым](07-self-employed.md).

```python
payout = kassa.payouts.create({
    "amount": {"value": "280.00", "currency": "RUB"},
    "payout_destination_data": {
        "type": "bank_card",
        "card": {"number": "5555555555554477"},
    },
    "self_employed": {"id": "se-285e5ee7-0022-5000-8000-01516a44b147"},
    "receipt_data": {
        "service": [{"amount": {"value": "280.00", "currency": "RUB"}}],
        "amount": {"value": "280.00", "currency": "RUB"},
    },
    "description": "Выплата за услугу",
})
```

## Выплата по токену

Когда реквизиты получателя собраны через виджет, вместо них передаётся токен.
Так номер карты не проходит через ваш сервер.

```python
payout = kassa.payouts.create({
    "amount": {"value": "280.00", "currency": "RUB"},
    "payout_token": "<токен из виджета>",
    "description": "Выплата по заказу №37",
})
```

## Информация о выплате

```python
payout = kassa.payouts.get("po-285e5ee7-0022-5000-8000-01516a44b147")

payout.status
payout.amount.value
payout.created_at
payout.succeeded_at
payout.is_succeeded

if payout.status == "canceled":
    print(payout.cancellation_details.party)
    print(payout.cancellation_details.reason)
```

## Список выплат

```python
page = kassa.payouts.list(status="succeeded", limit=20)

for payout in page:
    print(payout.id, payout.amount.value)
```

```python
for payout in kassa.payouts.iterate(status="succeeded"):
    print(payout.id)
```

## Поиск выплат

Отдельный эндпоинт, в котором доступен фильтр по метаданным.

```python
page = kassa.payouts.search(
    metadata="order_id:37",
    created_at_gte="2026-08-01T00:00:00.000Z",
    limit=20,
)

for payout in page:
    print(payout.id, payout.metadata)
```

Асинхронно:

```python
page = await kassa.payouts.search(metadata="order_id:37")
```
