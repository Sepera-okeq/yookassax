# Payouts

A payout moves money from the shop balance to a recipient: a card, a YooMoney
wallet or through the Faster Payments System (SBP).

* [Payout to a bank card](#payout-to-a-bank-card)
* [Payout through SBP](#payout-through-sbp)
* [Payout to a YooMoney wallet](#payout-to-a-yoomoney-wallet)
* [Payout to a self-employed person](#payout-to-a-self-employed-person)
* [Payout by token](#payout-by-token)
* [Payout details](#payout-details)
* [Listing payouts](#listing-payouts)
* [Searching payouts](#searching-payouts)

Payouts need a separate access key; a shop secret key does not work here.

## Payout to a bank card

```python
payout = kassa.payouts.create({
    "amount": {"value": "280.00", "currency": "RUB"},
    "payout_destination_data": {
        "type": "bank_card",
        "card": {"number": "5555555555554477"},
    },
    "description": "Payout for order 37",
    "metadata": {"order_id": "37"},
})

print(payout.id)
print(payout.status)   # pending, succeeded, canceled
```

Asynchronously:

```python
payout = await kassa.payouts.create({
    "amount": {"value": "280.00", "currency": "RUB"},
    "payout_destination_data": {
        "type": "bank_card",
        "card": {"number": "5555555555554477"},
    },
})
```

## Payout through SBP

The recipient is identified by phone number and bank from the
[SBP directory](09-sbp-banks.md). Personal data must be submitted in advance,
see the [personal data guide](08-personal-data.md).

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
    "description": "Payout for order 37",
})
```

## Payout to a YooMoney wallet

```python
payout = kassa.payouts.create({
    "amount": {"value": "280.00", "currency": "RUB"},
    "payout_destination_data": {
        "type": "yoo_money",
        "account_number": "410011758831136",
    },
    "description": "Payout for order 37",
})
```

## Payout to a self-employed person

The person must be registered in advance, see the
[self-employed guide](07-self-employed.md).

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
    "description": "Payout for a service",
})
```

## Payout by token

When the recipient details are collected through a widget, a token is sent
instead. The card number never touches your server.

```python
payout = kassa.payouts.create({
    "amount": {"value": "280.00", "currency": "RUB"},
    "payout_token": "<token from the widget>",
    "description": "Payout for order 37",
})
```

## Payout details

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

## Listing payouts

```python
page = kassa.payouts.list(status="succeeded", limit=20)

for payout in page:
    print(payout.id, payout.amount.value)
```

```python
for payout in kassa.payouts.iterate(status="succeeded"):
    print(payout.id)
```

## Searching payouts

A separate endpoint that supports filtering by metadata.

```python
page = kassa.payouts.search(
    metadata="order_id:37",
    created_at_gte="2026-08-01T00:00:00.000Z",
    limit=20,
)

for payout in page:
    print(payout.id, payout.metadata)
```

Asynchronously:

```python
page = await kassa.payouts.search(metadata="order_id:37")
```
