# Тестовый магазин

В тестовом магазине всё проходит как при настоящих платежах, но деньги никуда
не переводятся. Это единственный способ отладить интеграцию, не трогая
реальные деньги.

* [Как отличить тестовый магазин](#как-отличить-тестовый-магазин)
* [Что доступно в тестовом режиме](#что-доступно-в-тестовом-режиме)
* [Защита от боевых ключей](#защита-от-боевых-ключей)
* [Тестовый платёж](#тестовый-платёж)
* [Подмена HTTP в своих тестах](#подмена-http-в-своих-тестах)
* [Прогон по живому магазину](#прогон-по-живому-магазину)

## Как отличить тестовый магазин

По ответу `GET /me` и по полю `test` у объектов.

```python
settings = kassa.settings.get()

print(settings.test)          # True у тестового магазина
print(settings.account_id)
print(settings.status)        # enabled
```

Секретный ключ тестового магазина начинается с `test_`, боевой - с `live_`.
Проверять лучше и то, и другое: префикс ключа виден до первого запроса,
`settings.test` подтверждает уже со стороны ЮKassa.

## Что доступно в тестовом режиме

Тестовый магазин умеет меньше боевого, и это не ошибка интеграции:

```python
print(settings.payment_methods)   # ['yoo_money', 'bank_card']
```

Из способов оплаты доступны только банковская карта и ЮMoney. Выплаты,
Безопасная сделка, справочник банков СБП, персональные данные и самозанятые
требуют отдельного подключения и без него отвечают 401 или 403.

Список способов оплаты для интерфейса берите из `settings.payment_methods`, а
не из своего представления о ЮKassa: он отличается у каждого магазина.

## Защита от боевых ключей

Самая дорогая ошибка в тестах - случайно уехать в боевой магазин. Проверка
занимает три строки и стоит того.

```python
def build_client(shop_id: str, secret_key: str) -> YooKassa:
    """Клиент для тестов: боевой ключ не принимаем."""
    if not secret_key.startswith("test_"):
        raise RuntimeError("нужен ключ тестового магазина: тесты создают платежи")
    return YooKassa(shop_id=shop_id, secret_key=secret_key)
```

И то же самое после первого запроса, уже по ответу ЮKassa:

```python
settings = kassa.settings.get()
assert settings.test is True, "боевой магазин, платежи настоящие"
```

## Тестовый платёж

Создаётся как обычный. В ответе `test` равен `True`:

```python
payment = kassa.payments.create(
    {
        "amount": {"value": "2.00", "currency": "RUB"},
        "confirmation": {
            "type": "redirect",
            "return_url": "https://www.example.com/return_url",
        },
        "capture": True,
        "description": "Заказ №1",
    }
)

print(payment.test)               # True
print(payment.status)             # pending
print(payment.confirmation_url)   # сюда ведём плательщика
```

Платёж останется в `pending`, пока кто-то не пройдёт по `confirmation_url` и не
подтвердит оплату тестовой картой. Само по себе создание платежа его не
завершает, поэтому автоматический тест на `capture` или `cancel` без ручного
шага не сделать: до `waiting_for_capture` платёж без плательщика не доходит.

## Подмена HTTP в своих тестах

Для проверки собственной логики ходить в сеть не нужно и вредно: тесты
становятся медленными и зависят от чужой доступности. HTTP подменяется через
`respx`, так устроены и тесты самой библиотеки.

```python
import httpx
import respx

from yookassax import YooKassa


@respx.mock
def test_order_is_marked_paid():
    respx.post("https://api.yookassa.ru/v3/payments").mock(
        return_value=httpx.Response(
            200,
            json={
                "id": "22d6d597-000f-5000-9000-145f6df21d6f",
                "status": "succeeded",
                "paid": True,
                "amount": {"value": "2.00", "currency": "RUB"},
                "test": True,
            },
        )
    )

    with YooKassa(shop_id="123456", secret_key="test_secret") as kassa:
        payment = kassa.payments.create({"amount": {"value": "2.00", "currency": "RUB"}})

    assert payment.is_succeeded
```

Так же проверяются ветки, которые в живом магазине не воспроизвести: отмена,
подтверждение, ошибки 429 и 500, обрыв связи.

```python
@respx.mock
def test_retry_on_server_error():
    route = respx.post("https://api.yookassa.ru/v3/payments")
    route.side_effect = [
        httpx.Response(500, json={"code": "internal_server_error"}),
        httpx.Response(200, json={"id": "p-1", "status": "pending"}),
    ]

    with YooKassa(shop_id="123456", secret_key="test_secret") as kassa:
        payment = kassa.payments.create({"amount": {"value": "2.00", "currency": "RUB"}})

    assert payment.id == "p-1"
    assert route.call_count == 2
```

## Прогон по живому магазину

У библиотеки есть отдельный набор тестов, который идёт в настоящее API. Без
ключей он пропускается целиком, поэтому обычный прогон и CI его не замечают.

```bash
export YOOKASSA_SHOP_ID=... YOOKASSA_SECRET_KEY=test_...
pytest tests/integration
```

Главный тест там - `test_real_responses_have_no_unknown_fields`: он разбирает
реальные ответы магазина и требует, чтобы у каждого поля нашлось место в
моделях. Смысл в том, что спецификация OpenAPI отстаёт от API - именно так
нашлись поля `protocol`, `method_completed` и `challenge_completed` у 3-D
Secure, которых в спецификации нет вовсе.

Тот же приём полезен и в вашем приложении: раз в какое-то время разбирать
реальные ответы и смотреть, не появилось ли `UnknownFieldWarning`. Подробнее -
в [примерах по ошибкам](14-errors.md#поля-которых-нет-в-модели).
