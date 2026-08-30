# SBP banks

A directory of banks available for payouts through the Faster Payments System.
The bank identifier from this list is required when creating a payout.

## Fetching the list

```python
page = kassa.sbp_banks.list()

for bank in page:
    print(bank.bank_id, bank.name, bank.bic)
```

Asynchronously:

```python
page = await kassa.sbp_banks.list()
```

## Finding a bank by name

```python
def find_bank(banks, name_part: str):
    """The first bank whose name contains the substring."""
    needle = name_part.casefold()
    for bank in banks:
        if bank.name and needle in bank.name.casefold():
            return bank
    return None

banks = kassa.sbp_banks.list()
sberbank = find_bank(banks, "sber")

if sberbank is not None:
    payout = kassa.payouts.create({
        "amount": {"value": "280.00", "currency": "RUB"},
        "payout_destination_data": {
            "type": "sbp",
            "phone": "79001002030",
            "bank_id": sberbank.bank_id,
        },
    })
```

The list changes rarely, so it is reasonable to cache it on your side instead
of fetching it before every payout.
