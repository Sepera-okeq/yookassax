# Deals

A safe deal holds the buyer's money until the seller has fulfilled the
obligations. Only then the funds go to the seller as a payout.

* [Creating a deal](#creating-a-deal)
* [Payment attached to a deal](#payment-attached-to-a-deal)
* [Paying the seller](#paying-the-seller)
* [Deal details](#deal-details)
* [Listing deals](#listing-deals)
* [The full flow](#the-full-flow)

## Creating a deal

```python
deal = kassa.deals.create({
    "type": "safe_deal",
    "fee_moment": "payment_succeeded",
    "description": "Deal for order 88",
    "metadata": {"order_id": "88"},
})

print(deal.id)
print(deal.status)   # opened
```

Asynchronously:

```python
deal = await kassa.deals.create({
    "type": "safe_deal",
    "fee_moment": "payment_succeeded",
    "description": "Deal for order 88",
})
```

The `fee_moment` field decides when the commission is withheld:
`payment_succeeded` on payment or `deal_closed` when the deal closes.

## Payment attached to a deal

The payment is created as usual but references the deal and splits the amount
between the seller and the platform.

```python
payment = kassa.payments.create({
    "amount": {"value": "1000.00", "currency": "RUB"},
    "confirmation": {
        "type": "redirect",
        "return_url": "https://merchant-site.com/return_url",
    },
    "capture": True,
    "description": "Order 88",
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

## Paying the seller

After a successful payment the money sits on the deal balance. A payout moves
it to the seller.

```python
payout = kassa.payouts.create({
    "amount": {"value": "1000.00", "currency": "RUB"},
    "payout_token": "<seller token>",
    "description": "Payout for order 88",
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

## Deal details

```python
deal = kassa.deals.get("dl-285e5ee7-0022-5000-8000-01516a44b147")

deal.status            # opened, closed
deal.balance.value     # how much the deal holds
deal.payout_balance    # how much is available for payout
deal.fee_moment
deal.created_at
deal.expires_at
deal.metadata
```

## Listing deals

```python
page = kassa.deals.list(status="opened", limit=20)

for deal in page:
    print(deal.id, deal.status, deal.balance.value)
```

```python
for deal in kassa.deals.iterate(status="opened"):
    print(deal.id)
```

Asynchronously:

```python
async for deal in kassa.deals.iterate(status="opened"):
    print(deal.id)
```

## The full flow

```python
from yookassax import AsyncYooKassa

async def sell_through_safe_deal(order_id: str, seller_payout_token: str) -> None:
    async with AsyncYooKassa(shop_id="123456", secret_key="live_...") as kassa:
        # 1. Open a deal.
        deal = await kassa.deals.create({
            "type": "safe_deal",
            "fee_moment": "payment_succeeded",
            "description": f"Deal for order {order_id}",
            "metadata": {"order_id": order_id},
        })

        # 2. Create a payment attached to the deal.
        payment = await kassa.payments.create({
            "amount": {"value": "1000.00", "currency": "RUB"},
            "confirmation": {
                "type": "redirect",
                "return_url": "https://merchant-site.com/return_url",
            },
            "capture": True,
            "deal": {
                "id": deal.id,
                "settlements": [
                    {"type": "payout", "amount": {"value": "1000.00", "currency": "RUB"}},
                ],
            },
        }, idempotency_key=f"deal-payment-{order_id}")

        # 3. Send the payer to the confirmation URL and wait for payment.succeeded.
        redirect_user_to(payment.confirmation_url)

        # 4. Once the seller has delivered, pay them.
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

The idempotency keys here are not decorative: the flow is long, and retrying a
step after a failure must not create a second deal, a second payment or a
second payout.
