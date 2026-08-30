# Incoming notifications

A notification is a POST from YooKassa to your URL. The body is **not signed**,
so you must not make money decisions based on its contents.

* [Processing order](#processing-order)
* [FastAPI](#fastapi)
* [Django](#django)
* [Flask](#flask)
* [Handler idempotency](#handler-idempotency)
* [Event list](#event-list)

## Processing order

1. Verify the sender address.
2. Parse the body and find out which event arrived.
3. Fetch the object through the API and decide based on the API response.
4. Answer 200 as fast as possible.

Step three is mandatory. The amount in the body directly drives money, and
forging it is easier than it seems: it is enough for the request to pass
through your own proxy or for the sender address to be spoofed.

Step four is not a formality either: until you answer, YooKassa treats the
delivery as failed and repeats it. Move heavy work to a background task.

## FastAPI

```python
from fastapi import FastAPI, Request, Response
from yookassax import AsyncYooKassa, webhooks

app = FastAPI()
kassa = AsyncYooKassa(shop_id="123456", secret_key="live_...")


@app.post("/webhook")
async def handle_notification(request: Request):
    # 1. The trustworthy sender address is set by nginx in X-Real-IP.
    #    The leftmost X-Forwarded-For element is supplied by the client,
    #    so it must not be used.
    client_ip = request.headers.get("X-Real-IP", "")
    if not webhooks.is_trusted_ip(client_ip):
        return Response(status_code=403)

    # 2. Parse the body.
    notification = webhooks.parse(await request.json())

    # 3. The source of truth is the API response, not the notification body.
    if notification.is_payment_succeeded:
        payment = await kassa.payments.get(notification.object.id)
        if payment.is_succeeded:
            await mark_order_paid(payment.metadata["order_id"], payment.amount.value)

    elif notification.is_refund_succeeded:
        refund = await kassa.refunds.get(notification.object.id)
        if refund.is_succeeded:
            await mark_order_refunded(refund.payment_id)

    # 4. Answer quickly.
    return {"ok": True}
```

## Django

```python
import json

from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from yookassax import YooKassa, webhooks

kassa = YooKassa(shop_id="123456", secret_key="live_...")


@csrf_exempt
@require_POST
def handle_notification(request):
    client_ip = request.META.get("HTTP_X_REAL_IP", "")
    if not webhooks.is_trusted_ip(client_ip):
        return HttpResponse(status=403)

    notification = webhooks.parse(json.loads(request.body))

    if notification.is_payment_succeeded:
        payment = kassa.payments.get(notification.object.id)
        if payment.is_succeeded:
            mark_order_paid(payment.metadata["order_id"])

    return JsonResponse({"ok": True})
```

## Flask

```python
from flask import Flask, request, jsonify
from yookassax import YooKassa, webhooks

app = Flask(__name__)
kassa = YooKassa(shop_id="123456", secret_key="live_...")


@app.post("/webhook")
def handle_notification():
    client_ip = request.headers.get("X-Real-IP", "")
    if not webhooks.is_trusted_ip(client_ip):
        return "", 403

    notification = webhooks.parse(request.get_json(force=True))

    if notification.is_payment_succeeded:
        payment = kassa.payments.get(notification.object.id)
        if payment.is_succeeded:
            mark_order_paid(payment.metadata["order_id"])

    return jsonify(ok=True)
```

## Handler idempotency

YooKassa repeats delivery unless it receives a 200. The handler must tolerate
repeats: the same event will arrive several times.

A simple approach is to check the current order state before changing it.

```python
async def mark_order_paid(order_id: str, amount) -> None:
    order = await load_order(order_id)

    # Already handled: return quietly instead of crediting twice.
    if order.is_paid:
        return

    await save_order_paid(order_id, amount)
```

Relying on the database is more robust: a unique index on the payment
identifier prevents recording a credit twice even when two copies of the
notification arrive at the same time.

## Event list

```python
from yookassax.webhooks import EVENTS

print(EVENTS)
```

| Event | When it arrives |
|---|---|
| `payment.succeeded` | the payment went through, the money is with the shop |
| `payment.waiting_for_capture` | funds are held, capture or cancel is required |
| `payment.canceled` | the payment was cancelled |
| `refund.succeeded` | the refund went through |
| `payout.succeeded` | the payout reached the recipient |
| `payout.canceled` | the payout was rejected |
| `deal.closed` | the deal was closed |

An unknown event does not break parsing: `object` stays a dictionary. This is
deliberate, otherwise a new event from YooKassa would cause a failure to handle
the notification and endless redeliveries.

```python
notification = webhooks.parse(body)

if notification.event not in EVENTS:
    logger.info("Unknown event: %s", notification.event)
    return {"ok": True}   # answer 200 anyway
```
