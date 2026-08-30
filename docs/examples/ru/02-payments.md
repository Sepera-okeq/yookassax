# Платежи

Платёж это центральный объект API. У него линейный жизненный цикл: он
последовательно переходит из статуса в статус.

* [Создание платежа](#создание-платежа)
* [Платёж с чеком](#платёж-с-чеком)
* [Двухстадийный платёж](#двухстадийный-платёж)
* [Частичное подтверждение](#частичное-подтверждение)
* [Отмена платежа](#отмена-платежа)
* [Информация о платеже](#информация-о-платеже)
* [Список платежей с фильтрацией](#список-платежей-с-фильтрацией)
* [Платёж по сохранённому способу оплаты](#платёж-по-сохранённому-способу-оплаты)
* [Платёж с чеком за ЖКУ](#платёж-с-чеком-за-жку)

## Создание платежа

```python
payment = kassa.payments.create({
    "amount": {"value": "1000.00", "currency": "RUB"},
    "confirmation": {
        "type": "redirect",
        "return_url": "https://merchant-site.ru/return_url",
    },
    "capture": True,
    "description": "Заказ №72",
    "metadata": {"order_number": "72"},
})

print(payment.id)
print(payment.status)             # pending
print(payment.confirmation_url)   # сюда ведём плательщика
```

Асинхронно:

```python
payment = await kassa.payments.create({
    "amount": {"value": "1000.00", "currency": "RUB"},
    "confirmation": {
        "type": "redirect",
        "return_url": "https://merchant-site.ru/return_url",
    },
    "capture": True,
    "description": "Заказ №72",
})
```

Сумму передавайте строкой, а не числом с плавающей точкой: `"1000.00"`, а не
`1000.0`. В ответе она приходит как `Decimal`.

Ключ идемпотентности проставляется автоматически. Свой имеет смысл задавать,
когда повтор возможен со стороны вашего кода:

```python
payment = kassa.payments.create(params, idempotency_key=f"order-{order_id}")
```

Второй вызов с тем же ключом вернёт уже созданный платёж, а не создаст новый.

## Платёж с чеком

Чек формируется вместе с платежом, если магазин работает по 54-ФЗ.

```python
payment = kassa.payments.create({
    "amount": {"value": "1000.00", "currency": "RUB"},
    "confirmation": {
        "type": "redirect",
        "return_url": "https://merchant-site.ru/return_url",
    },
    "capture": True,
    "description": "Заказ №72",
    "receipt": {
        "customer": {
            "full_name": "Иванов Иван Иванович",
            "email": "email@email.ru",
            "phone": "79211234567",
            "inn": "6321341814",
        },
        "items": [
            {
                "description": "Переносное зарядное устройство",
                "quantity": "1.00",
                "amount": {"value": "1000.00", "currency": "RUB"},
                "vat_code": "2",
                "payment_mode": "full_payment",
                "payment_subject": "commodity",
                "country_of_origin_code": "CN",
            },
        ],
    },
})
```

## Двухстадийный платёж

При `capture=False` деньги холдируются на карте плательщика, но не списываются.
Подтвердить или отменить нужно в отведённое время, иначе платёж отменится сам и
деньги вернутся.

```python
payment = kassa.payments.create({
    "amount": {"value": "1000.00", "currency": "RUB"},
    "confirmation": {
        "type": "redirect",
        "return_url": "https://merchant-site.ru/return_url",
    },
    "capture": False,
    "description": "Заказ №72",
})

# позже, когда товар готов к выдаче
if payment.is_waiting_for_capture:
    payment = kassa.payments.capture(payment.id)
    print(payment.status)   # succeeded
```

Асинхронно:

```python
payment = await kassa.payments.capture(payment.id)
```

## Частичное подтверждение

Подтвердить можно сумму меньше исходной. Остаток вернётся плательщику.

```python
payment = kassa.payments.capture(
    "21b23b5b-000f-5061-a000-0674e49a8c10",
    {"amount": {"value": "800.00", "currency": "RUB"}},
)
```

С разделением между продавцами в маркетплейсе:

```python
payment = kassa.payments.capture(
    "21b23b5b-000f-5061-a000-0674e49a8c10",
    {
        "amount": {"value": "1000.00", "currency": "RUB"},
        "transfers": [
            {"account_id": "123", "amount": {"value": "300.00", "currency": "RUB"}},
            {"account_id": "456", "amount": {"value": "700.00", "currency": "RUB"}},
        ],
    },
)
```

## Отмена платежа

Отменяется платёж в статусе `waiting_for_capture`. Для карт и кошелька ЮMoney
деньги возвращаются мгновенно, для остальных способов до нескольких дней.

```python
payment = kassa.payments.cancel("21b23b5b-000f-5061-a000-0674e49a8c10")
print(payment.status)   # canceled
```

```python
payment = await kassa.payments.cancel("21b23b5b-000f-5061-a000-0674e49a8c10")
```

## Информация о платеже

```python
payment = kassa.payments.get("21b23b5b-000f-5061-a000-0674e49a8c10")

payment.status                  # pending, waiting_for_capture, succeeded, canceled
payment.amount.value            # Decimal("1000.00")
payment.amount.currency         # "RUB"
payment.created_at              # datetime с часовым поясом
payment.paid                    # bool
payment.refundable              # можно ли вернуть
payment.metadata                # словарь, который вы передали при создании

payment.is_pending
payment.is_waiting_for_capture
payment.is_succeeded
payment.is_canceled
```

Если платёж отменён, причина лежит в `cancellation_details`:

```python
if payment.is_canceled:
    print(payment.cancellation_details.party)    # кто отменил
    print(payment.cancellation_details.reason)   # почему
```

Поле, которого ещё нет в модели, доступно так:

```python
payment.extra("новое_поле_из_api")
```

О таком поле библиотека один раз предупредит: значит, ЮKassa расширила ответ и
стоит обновить `yookassax`. Подробности в
[примерах по ошибкам](14-errors.md#поля-которых-нет-в-модели).

## Список платежей с фильтрацией

Страницей:

```python
page = kassa.payments.list(
    status="succeeded",
    limit=50,
    created_at_gte="2026-08-01T00:00:00.000Z",
    created_at_lt="2026-09-01T00:00:00.000Z",
)

for payment in page:
    print(payment.id, payment.amount.value)

print(page.next_cursor)
print(page.has_more)
```

Следующая страница:

```python
next_page = kassa.payments.list(status="succeeded", cursor=page.next_cursor)
```

Целиком, без ручного перелистывания:

```python
for payment in kassa.payments.iterate(status="succeeded"):
    print(payment.id)
```

Асинхронно:

```python
async for payment in kassa.payments.iterate(status="succeeded"):
    print(payment.id)
```

Фильтры совпадают с документацией API. Точки в именах параметров заменяются на
подчёркивания: `created_at.gte` становится `created_at_gte`.

## Платёж по сохранённому способу оплаты

Списание без участия плательщика. Способ оплаты должен быть сохранён заранее,
см. [примеры по способам оплаты](11-payment-methods.md).

```python
payment = kassa.payments.create({
    "amount": {"value": "1000.00", "currency": "RUB"},
    "payment_method_id": "1da5c87d-0984-50e8-a7f3-8de646dd9ec9",
    "capture": True,
    "description": "Продление подписки",
})
```

Здесь `confirmation` не нужен: редиректа не будет, `confirmation_url` вернётся
пустым.

Если магазину не подключены рекуррентные платежи, ЮKassa ответит 403:

```python
from yookassax import Forbidden

try:
    payment = kassa.payments.create({...})
except Forbidden as error:
    print("Рекуррентные платежи не подключены:", error.description)
```

## Платёж с чеком за ЖКУ

```python
payment = kassa.payments.create({
    "amount": {"value": "100.00", "currency": "RUB"},
    "confirmation": {
        "type": "redirect",
        "return_url": "https://merchant-site.ru/return_url",
    },
    "capture": True,
    "payment_order": {
        "type": "utilities",
        "amount": {"value": "100.00", "currency": "RUB"},
        "payment_purpose": "Оплата ЖКУ за июль 2026",
        "recipient": {
            "name": "ООО УК Жилфонд",
            "inn": "6321341814",
            "kpp": "987654321",
            "bank": {
                "name": "ПАО Сбербанк",
                "bic": "044525225",
                "account": "40702810000000000001",
                "correspondent_account": "30101810400000000225",
            },
        },
        "kbk": "18210102000011000110",
        "oktmo": "45382000",
        "payment_period": {"month": 7, "year": 2026},
        "account_number": "1234567890",
    },
})
```
