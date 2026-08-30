# Входящие уведомления

Уведомление это POST от ЮKassa на ваш URL. Тело **не подписано**, поэтому
принимать решения о деньгах по его содержимому нельзя.

* [Порядок обработки](#порядок-обработки)
* [FastAPI](#fastapi)
* [Django](#django)
* [Flask](#flask)
* [Идемпотентность обработчика](#идемпотентность-обработчика)
* [Список событий](#список-событий)

## Порядок обработки

1. Проверить адрес отправителя.
2. Разобрать тело и понять, какое событие пришло.
3. Запросить объект через API и принимать решение по ответу API.
4. Ответить 200 как можно быстрее.

Третий шаг обязателен. Сумма из тела напрямую управляет деньгами, а подделать
её проще, чем кажется: достаточно, чтобы запрос прошёл через ваш же прокси или
чтобы адрес отправителя оказался подменён.

Четвёртый шаг тоже не формальность: пока вы не ответили, ЮKassa считает
доставку неудачной и повторяет её. Тяжёлую работу выносите в фоновую задачу.

## FastAPI

```python
from fastapi import FastAPI, Request, Response
from yookassax import AsyncYooKassa, webhooks

app = FastAPI()
kassa = AsyncYooKassa(shop_id="123456", secret_key="live_...")


@app.post("/webhook")
async def handle_notification(request: Request):
    # 1. Достоверный адрес отправителя ставит nginx в X-Real-IP.
    #    Левый элемент X-Forwarded-For подставляет клиент, брать его нельзя.
    client_ip = request.headers.get("X-Real-IP", "")
    if not webhooks.is_trusted_ip(client_ip):
        return Response(status_code=403)

    # 2. Разбираем тело.
    notification = webhooks.parse(await request.json())

    # 3. Источник истины это ответ API, а не тело уведомления.
    if notification.is_payment_succeeded:
        payment = await kassa.payments.get(notification.object.id)
        if payment.is_succeeded:
            await mark_order_paid(payment.metadata["order_id"], payment.amount.value)

    elif notification.is_refund_succeeded:
        refund = await kassa.refunds.get(notification.object.id)
        if refund.is_succeeded:
            await mark_order_refunded(refund.payment_id)

    # 4. Отвечаем быстро.
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

## Идемпотентность обработчика

ЮKassa повторяет доставку, если не получила 200. Обработчик обязан выдерживать
повторы: одно и то же событие придёт несколько раз.

Простой способ: проверять текущее состояние заказа перед изменением.

```python
async def mark_order_paid(order_id: str, amount) -> None:
    order = await load_order(order_id)

    # Уже обработан: выходим молча, не начисляя второй раз.
    if order.is_paid:
        return

    await save_order_paid(order_id, amount)
```

Надёжнее опереться на базу: уникальный индекс по идентификатору платежа не даст
записать зачисление дважды даже при одновременной доставке двух копий
уведомления.

## Список событий

```python
from yookassax.webhooks import EVENTS

print(EVENTS)
```

| Событие | Когда приходит |
|---|---|
| `payment.succeeded` | платёж прошёл, деньги у магазина |
| `payment.waiting_for_capture` | деньги захолдированы, нужен capture или cancel |
| `payment.canceled` | платёж отменён |
| `refund.succeeded` | возврат прошёл |
| `payout.succeeded` | выплата дошла до получателя |
| `payout.canceled` | выплата отклонена |
| `deal.closed` | сделка закрыта |

Неизвестное событие разбор не роняет: `object` останется словарём. Это
намеренно, иначе новое событие от ЮKassa приводило бы к отказу обработать
уведомление и к бесконечным повторам.

```python
notification = webhooks.parse(body)

if notification.event not in EVENTS:
    logger.info("Неизвестное событие: %s", notification.event)
    return {"ok": True}   # всё равно отвечаем 200
```
