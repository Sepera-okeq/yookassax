# Personal data

Recipient personal data is submitted to YooKassa separately from the payout and
stored there for a limited time. The payout itself only references an
identifier.

* [Submitting SBP recipient data](#submitting-sbp-recipient-data)
* [Submitted data details](#submitted-data-details)
* [Using it in a payout](#using-it-in-a-payout)

## Submitting SBP recipient data

```python
personal_data = kassa.personal_data.create({
    "type": "sbp_payout_recipient",
    "last_name": "Ivanov",
    "first_name": "Ivan",
    "middle_name": "Ivanovich",
    "metadata": {"email": "i.ivanov@ivan.name"},
})

print(personal_data.id)
print(personal_data.status)      # active, canceled
print(personal_data.expires_at)  # when the data will be deleted
```

Asynchronously:

```python
personal_data = await kassa.personal_data.create({
    "type": "sbp_payout_recipient",
    "last_name": "Ivanov",
    "first_name": "Ivan",
})
```

## Submitted data details

```python
personal_data = kassa.personal_data.get("pd-285e5ee7-0022-5000-8000-01516a44b147")

personal_data.status
personal_data.expires_at

if personal_data.status == "canceled":
    print(personal_data.cancellation_details.reason)
```

Mind `expires_at`: after that moment the data is deleted, and a new payout will
require submitting it again.

## Using it in a payout

```python
payout = kassa.payouts.create({
    "amount": {"value": "280.00", "currency": "RUB"},
    "payout_destination_data": {
        "type": "sbp",
        "phone": "79001002030",
        "bank_id": "100000000111",
    },
    "personal_data": [{"id": personal_data.id}],
    "description": "Payout for order 37",
})
```
