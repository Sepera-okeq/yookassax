# Персональные данные

Персональные данные получателя передаются в ЮKassa отдельно от выплаты и
хранятся там ограниченное время. В самой выплате указывается только
идентификатор.

* [Передача данных получателя СБП](#передача-данных-получателя-сбп)
* [Информация о переданных данных](#информация-о-переданных-данных)
* [Использование в выплате](#использование-в-выплате)

## Передача данных получателя СБП

```python
personal_data = kassa.personal_data.create({
    "type": "sbp_payout_recipient",
    "last_name": "Иванов",
    "first_name": "Иван",
    "middle_name": "Иванович",
    "metadata": {"email": "i.ivanov@ivan.name"},
})

print(personal_data.id)
print(personal_data.status)      # active, canceled
print(personal_data.expires_at)  # когда данные будут удалены
```

Асинхронно:

```python
personal_data = await kassa.personal_data.create({
    "type": "sbp_payout_recipient",
    "last_name": "Иванов",
    "first_name": "Иван",
})
```

## Информация о переданных данных

```python
personal_data = kassa.personal_data.get("pd-285e5ee7-0022-5000-8000-01516a44b147")

personal_data.status
personal_data.expires_at

if personal_data.status == "canceled":
    print(personal_data.cancellation_details.reason)
```

Обратите внимание на `expires_at`: после этого момента данные удаляются, и для
новой выплаты их придётся передать заново.

## Использование в выплате

```python
payout = kassa.payouts.create({
    "amount": {"value": "280.00", "currency": "RUB"},
    "payout_destination_data": {
        "type": "sbp",
        "phone": "79001002030",
        "bank_id": "100000000111",
    },
    "personal_data": [{"id": personal_data.id}],
    "description": "Выплата по заказу №37",
})
```
