# Способы оплаты

Сохранённый способ оплаты позволяет списывать деньги повторно без участия
плательщика: подписки, автоплатежи, оплата в один клик.

* [Сохранение способа оплаты](#сохранение-способа-оплаты)
* [Сохранение при первом платеже](#сохранение-при-первом-платеже)
* [Информация о способе оплаты](#информация-о-способе-оплаты)
* [Списание по сохранённому способу](#списание-по-сохранённому-способу)

Магазину должны быть подключены рекуррентные платежи. Иначе ЮKassa ответит 403
и на сохранение, и на списание.

## Сохранение способа оплаты

Отдельный сценарий: плательщик привязывает карту, но денег в этот момент не
платит.

```python
method = kassa.payment_methods.create({
    "type": "bank_card",
    "client_ip": "1.2.3.4",
    "holder": {"gateway_id": "100700"},
    "confirmation": {
        "type": "redirect",
        "return_url": "https://merchant-site.ru/return_url",
    },
    "metadata": {"order_id": "order-72"},
})

print(method.id)
print(method.status)   # pending, active, inactive
print(method.saved)
```

Асинхронно:

```python
method = await kassa.payment_methods.create({
    "type": "bank_card",
    "client_ip": "1.2.3.4",
    "holder": {"gateway_id": "100700"},
    "confirmation": {
        "type": "redirect",
        "return_url": "https://merchant-site.ru/return_url",
    },
})
```

## Сохранение при первом платеже

Чаще способ сохраняют попутно, вместе с обычной оплатой.

```python
payment = kassa.payments.create({
    "amount": {"value": "1000.00", "currency": "RUB"},
    "confirmation": {
        "type": "redirect",
        "return_url": "https://merchant-site.ru/return_url",
    },
    "capture": True,
    "save_payment_method": True,
    "description": "Первый платёж по подписке",
})
```

После успешной оплаты идентификатор сохранённого способа лежит в платеже:

```python
payment = kassa.payments.get(payment.id)

if payment.is_succeeded and payment.payment_method and payment.payment_method.saved:
    saved_method_id = payment.payment_method.id
    # сохраните его у себя, он понадобится для следующих списаний
```

## Информация о способе оплаты

```python
method = kassa.payment_methods.get("1da5c87d-0984-50e8-a7f3-8de646dd9ec9")

method.type      # bank_card, sbp, yoo_money
method.status
method.saved
method.title     # например "Bank card *4444"
method.card      # маска карты, срок действия, банк-эмитент
```

## Списание по сохранённому способу

```python
payment = kassa.payments.create({
    "amount": {"value": "1000.00", "currency": "RUB"},
    "payment_method_id": saved_method_id,
    "capture": True,
    "description": "Продление подписки за сентябрь",
}, idempotency_key=f"subscription-{subscription_id}-2026-09")
```

Здесь `confirmation` не нужен: плательщик в списании не участвует, редиректа не
будет.

Ключ идемпотентности здесь особенно важен. Списания по подписке запускает
планировщик, а он может повторить задачу после сбоя. Ключ, собранный из
идентификатора подписки и периода, не даст списать дважды за один месяц.

Отказ обрабатывается так:

```python
from yookassax import Forbidden

try:
    payment = kassa.payments.create({...})
except Forbidden as error:
    # Рекуррентные платежи не подключены магазину.
    # Ошибка постоянная: повторять списание бессмысленно.
    print(error.description)
```
