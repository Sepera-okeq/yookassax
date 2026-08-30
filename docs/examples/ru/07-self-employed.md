# Самозанятые

Чтобы выплачивать деньги самозанятому, его нужно сначала зарегистрировать в
ЮKassa и дождаться подтверждения.

* [Регистрация самозанятого](#регистрация-самозанятого)
* [Регистрация с подтверждением по ссылке](#регистрация-с-подтверждением-по-ссылке)
* [Информация о самозанятом](#информация-о-самозанятом)

## Регистрация самозанятого

```python
self_employed = kassa.self_employed.create({
    "itn": "123456789012",
    "phone": "79001002030",
})

print(self_employed.id)
print(self_employed.status)   # pending, confirmed, canceled
```

Асинхронно:

```python
self_employed = await kassa.self_employed.create({
    "itn": "123456789012",
    "phone": "79001002030",
})
```

Достаточно передать либо ИНН, либо телефон. Оба поля вместе повышают шансы
найти человека в реестре самозанятых.

## Регистрация с подтверждением по ссылке

Самозанятый подтверждает согласие в приложении "Мой налог". Со сценарием
`redirect` ЮKassa вернёт ссылку, по которой его нужно провести.

```python
self_employed = kassa.self_employed.create({
    "itn": "123456789012",
    "phone": "79001002030",
    "confirmation": {"type": "redirect"},
})

if self_employed.confirmation:
    print(self_employed.confirmation.get("confirmation_url"))
```

## Информация о самозанятом

```python
self_employed = kassa.self_employed.get("se-285e5ee7-0022-5000-8000-01516a44b147")

self_employed.status      # confirmed означает, что можно платить
self_employed.itn
self_employed.phone
self_employed.created_at
```

Выплачивать деньги можно только при статусе `confirmed`:

```python
if self_employed.status != "confirmed":
    raise RuntimeError("Самозанятый ещё не подтвердил согласие")

payout = kassa.payouts.create({
    "amount": {"value": "280.00", "currency": "RUB"},
    "payout_destination_data": {
        "type": "bank_card",
        "card": {"number": "5555555555554477"},
    },
    "self_employed": {"id": self_employed.id},
    "receipt_data": {
        "service": [{"amount": {"value": "280.00", "currency": "RUB"}}],
        "amount": {"value": "280.00", "currency": "RUB"},
    },
})
```
