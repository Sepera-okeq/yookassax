# Настройка клиента

* [Аутентификация](#аутентификация)
* [Параметры клиента](#параметры-клиента)
* [Закрытие соединений](#закрытие-соединений)
* [Информация о магазине](#информация-о-магазине)
* [Работа с подписками на уведомления](#работа-с-подписками-на-уведомления)
* [Несколько магазинов в одном процессе](#несколько-магазинов-в-одном-процессе)

## Аутентификация

Свой магазин: пара идентификатора и секретного ключа.

```python
from yookassax import YooKassa

kassa = YooKassa(shop_id="123456", secret_key="live_...")
```

Асинхронно то же самое:

```python
from yookassax import AsyncYooKassa

kassa = AsyncYooKassa(shop_id="123456", secret_key="live_...")
```

Чужой магазин: OAuth-токен, который магазин выдал вашему приложению.

```python
kassa = YooKassa(oauth_token="токен")
```

Задать оба способа сразу нельзя, клиент откажется собираться:

```python
from yookassax import ConfigurationError

try:
    YooKassa(shop_id="123456", secret_key="live_...", oauth_token="токен")
except ConfigurationError as error:
    print(error)
```

Ошибка настройки поднимается сразу при создании клиента, а не на первом
платеже. Так неверные ключи обнаруживаются на старте приложения.

## Параметры клиента

```python
kassa = YooKassa(
    shop_id="123456",
    secret_key="live_...",
    timeout=30.0,   # таймаут одного запроса в секундах
    retries=3,      # всего попыток, считая первую
    api_url="https://api.yookassa.ru/v3",
)
```

`retries=1` означает не повторять вовсе. Подробнее о том, что именно
повторяется, в [примерах по ошибкам](14-errors.md).

## Закрытие соединений

Клиент держит пул соединений, поэтому его создают один раз на приложение, а не
на каждый запрос.

```python
with YooKassa(shop_id="123456", secret_key="live_...") as kassa:
    ...
```

```python
async with AsyncYooKassa(shop_id="123456", secret_key="live_...") as kassa:
    ...
```

Без контекстного менеджера закрывайте явно: `kassa.close()` у синхронного,
`await kassa.aclose()` у асинхронного.

В веб-приложении удобно держать один клиент на всё время жизни процесса.
Пример для FastAPI:

```python
from contextlib import asynccontextmanager
from fastapi import FastAPI
from yookassax import AsyncYooKassa

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.kassa = AsyncYooKassa(shop_id="123456", secret_key="live_...")
    yield
    await app.state.kassa.aclose()

app = FastAPI(lifespan=lifespan)
```

## Информация о магазине

```python
me = kassa.settings.get()

print(me.account_id)          # идентификатор магазина
print(me.test)                # True, если магазин тестовый
print(me.payment_methods)     # доступные способы оплаты
print(me.fiscalization)       # настройки фискализации
```

```python
me = await kassa.settings.get()
```

Вызов на старте приложения полезен: он сразу показывает, боевые ключи
подключены или тестовые. Иначе это выясняется на первом платеже.

## Работа с подписками на уведомления

Управление подписками работает только с OAuth-токеном. Секретный ключ магазина
такие запросы не выполняет.

```python
kassa = YooKassa(oauth_token="токен")

kassa.webhooks.add("payment.succeeded", "https://merchant-site.ru/webhook")
kassa.webhooks.add("refund.succeeded", "https://merchant-site.ru/webhook")

for webhook in kassa.webhooks.list():
    print(webhook.id, webhook.event, webhook.url)

kassa.webhooks.remove("wh-1da5c0de")
```

Асинхронно:

```python
await kassa.webhooks.add("payment.succeeded", "https://merchant-site.ru/webhook")
page = await kassa.webhooks.list()
await kassa.webhooks.remove("wh-1da5c0de")
```

Разбор самих уведомлений описан отдельно, в [примерах по
уведомлениям](13-webhooks.md).

## Несколько магазинов в одном процессе

Ключи принадлежат экземпляру клиента, поэтому магазины не мешают друг другу.

```python
shops = {
    "первый": YooKassa(shop_id="111", secret_key="live_a..."),
    "второй": YooKassa(shop_id="222", secret_key="live_b..."),
}

payment = shops["первый"].payments.create({...})
```

Это важное отличие от официального SDK: там ключи лежат в `Configuration` на
уровне класса, и при параллельных платежах два запроса могут переписать токен
друг другу. Платёж тогда уходит через чужой магазин.
