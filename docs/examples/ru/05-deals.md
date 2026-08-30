# Сделки

Безопасная сделка держит деньги покупателя до момента, когда продавец выполнил
обязательства. Только после этого средства уходят продавцу выплатой.

* [Создание сделки](#создание-сделки)
* [Платёж с привязкой к сделке](#платёж-с-привязкой-к-сделке)
* [Выплата продавцу по сделке](#выплата-продавцу-по-сделке)
* [Информация о сделке](#информация-о-сделке)
* [Список сделок](#список-сделок)
* [Полный сценарий целиком](#полный-сценарий-целиком)

## Создание сделки

```python
deal = kassa.deals.create({
    "type": "safe_deal",
    "fee_moment": "payment_succeeded",
    "description": "Сделка по заказу №88",
    "metadata": {"order_id": "88"},
})

print(deal.id)
print(deal.status)   # opened
```

Асинхронно:

```python
deal = await kassa.deals.create({
    "type": "safe_deal",
    "fee_moment": "payment_succeeded",
    "description": "Сделка по заказу №88",
})
```

Поле `fee_moment` определяет, когда удерживается комиссия: `payment_succeeded`
при оплате или `deal_closed` при закрытии сделки.

## Платёж с привязкой к сделке

Платёж создаётся как обычный, но с указанием сделки и разделением суммы между
продавцом и площадкой.

```python
payment = kassa.payments.create({
    "amount": {"value": "1000.00", "currency": "RUB"},
    "confirmation": {
        "type": "redirect",
        "return_url": "https://merchant-site.ru/return_url",
    },
    "capture": True,
    "description": "Заказ №88",
    "deal": {
        "id": deal.id,
        "settlements": [
            {
                "type": "payout",
                "amount": {"value": "1000.00", "currency": "RUB"},
            },
        ],
    },
})
```

## Выплата продавцу по сделке

После успешного платежа деньги лежат на балансе сделки. Выплата переводит их
продавцу.

```python
payout = kassa.payouts.create({
    "amount": {"value": "1000.00", "currency": "RUB"},
    "payout_token": "<токен продавца>",
    "description": "Выплата по заказу №88",
    "deal": {
        "id": deal.id,
        "settlements": [
            {
                "type": "payout",
                "amount": {"value": "1000.00", "currency": "RUB"},
            },
        ],
    },
})
```

## Информация о сделке

```python
deal = kassa.deals.get("dl-285e5ee7-0022-5000-8000-01516a44b147")

deal.status            # opened, closed
deal.balance.value     # сколько денег держит сделка
deal.payout_balance    # сколько доступно к выплате
deal.fee_moment
deal.created_at
deal.expires_at
deal.metadata
```

## Список сделок

```python
page = kassa.deals.list(status="opened", limit=20)

for deal in page:
    print(deal.id, deal.status, deal.balance.value)
```

```python
for deal in kassa.deals.iterate(status="opened"):
    print(deal.id)
```

Асинхронно:

```python
async for deal in kassa.deals.iterate(status="opened"):
    print(deal.id)
```

## Полный сценарий целиком

```python
from yookassax import AsyncYooKassa

async def sell_through_safe_deal(order_id: str, seller_payout_token: str) -> None:
    async with AsyncYooKassa(shop_id="123456", secret_key="live_...") as kassa:
        # 1. Открываем сделку.
        deal = await kassa.deals.create({
            "type": "safe_deal",
            "fee_moment": "payment_succeeded",
            "description": f"Сделка по заказу {order_id}",
            "metadata": {"order_id": order_id},
        })

        # 2. Создаём платёж, привязанный к сделке.
        payment = await kassa.payments.create({
            "amount": {"value": "1000.00", "currency": "RUB"},
            "confirmation": {
                "type": "redirect",
                "return_url": "https://merchant-site.ru/return_url",
            },
            "capture": True,
            "deal": {
                "id": deal.id,
                "settlements": [
                    {"type": "payout", "amount": {"value": "1000.00", "currency": "RUB"}},
                ],
            },
        }, idempotency_key=f"deal-payment-{order_id}")

        # 3. Ведём плательщика по ссылке и ждём уведомления payment.succeeded.
        redirect_user_to(payment.confirmation_url)

        # 4. Когда продавец выполнил обязательства, выплачиваем ему деньги.
        await kassa.payouts.create({
            "amount": {"value": "1000.00", "currency": "RUB"},
            "payout_token": seller_payout_token,
            "deal": {
                "id": deal.id,
                "settlements": [
                    {"type": "payout", "amount": {"value": "1000.00", "currency": "RUB"}},
                ],
            },
        }, idempotency_key=f"deal-payout-{order_id}")
```

Ключи идемпотентности здесь не декоративные: сценарий длинный, и повтор шага
после сбоя не должен создавать вторую сделку, второй платёж или вторую выплату.
