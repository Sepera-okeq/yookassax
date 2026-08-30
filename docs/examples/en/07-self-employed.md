# Self-employed

To pay a self-employed person, register them with YooKassa first and wait for
confirmation.

* [Registering a self-employed person](#registering-a-self-employed-person)
* [Registration with redirect confirmation](#registration-with-redirect-confirmation)
* [Self-employed details](#self-employed-details)

## Registering a self-employed person

```python
self_employed = kassa.self_employed.create({
    "itn": "123456789012",
    "phone": "79001002030",
})

print(self_employed.id)
print(self_employed.status)   # pending, confirmed, canceled
```

Asynchronously:

```python
self_employed = await kassa.self_employed.create({
    "itn": "123456789012",
    "phone": "79001002030",
})
```

Either the taxpayer number or the phone is enough. Both together improve the
chance of finding the person in the register.

## Registration with redirect confirmation

The person confirms consent in the "My Tax" application. With the `redirect`
scenario YooKassa returns a URL to send them to.

```python
self_employed = kassa.self_employed.create({
    "itn": "123456789012",
    "phone": "79001002030",
    "confirmation": {"type": "redirect"},
})

if self_employed.confirmation:
    print(self_employed.confirmation.get("confirmation_url"))
```

## Self-employed details

```python
self_employed = kassa.self_employed.get("se-285e5ee7-0022-5000-8000-01516a44b147")

self_employed.status      # confirmed means payouts are allowed
self_employed.itn
self_employed.phone
self_employed.created_at
```

Payouts are only possible in the `confirmed` status:

```python
if self_employed.status != "confirmed":
    raise RuntimeError("The person has not confirmed consent yet")

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
