# Банки СБП

Справочник банков, доступных для выплат через Систему быстрых платежей.
Идентификатор банка из этого списка нужен при создании выплаты.

## Получить список

```python
page = kassa.sbp_banks.list()

for bank in page:
    print(bank.bank_id, bank.name, bank.bic)
```

Асинхронно:

```python
page = await kassa.sbp_banks.list()
```

## Найти банк по названию

```python
def find_bank(banks, name_part: str):
    """Первый банк, в названии которого встречается подстрока."""
    needle = name_part.casefold()
    for bank in banks:
        if bank.name and needle in bank.name.casefold():
            return bank
    return None

banks = kassa.sbp_banks.list()
sberbank = find_bank(banks, "сбер")

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

Список меняется редко, поэтому его разумно кешировать у себя, а не запрашивать
перед каждой выплатой.
