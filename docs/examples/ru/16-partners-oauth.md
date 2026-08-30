# Партнёрская программа и OAuth

API для партнёров позволяет приложению (CRM, CMS, бот) работать с ЮKassa от
имени чужого магазина, не зная его секретный ключ. Магазин выдаёт приложению
OAuth-токен, приложение проводит платежи и возвраты.

* [Что нужно понимать до начала](#что-нужно-понимать-до-начала)
* [Шаг 1. Регистрация приложения](#шаг-1-регистрация-приложения)
* [Шаг 2. Ссылка на выдачу прав](#шаг-2-ссылка-на-выдачу-прав)
* [Шаг 3. Код подтверждения](#шаг-3-код-подтверждения)
* [Шаг 4. Обмен кода на токен](#шаг-4-обмен-кода-на-токен)
* [Шаг 5. Работа от имени магазина](#шаг-5-работа-от-имени-магазина)
* [Уведомления только по API](#уведомления-только-по-api)
* [Хранение и жизненный цикл токена](#хранение-и-жизненный-цикл-токена)
* [Права приложения](#права-приложения)
* [Тестирование](#тестирование)

## Что нужно понимать до начала

**Библиотека работает с готовым токеном.** Обмен кода на токен идёт на
OAuth-сервере ЮKassa (`https://yookassa.ru/oauth/v2/`), а не в API `/v3`,
поэтому здесь он делается напрямую через `httpx` - он уже стоит как
зависимость `yookassax`, ставить ничего не нужно.

**Токен даёт право двигать чужие деньги.** Его нельзя класть в cookie, в
логи, в репозиторий и в поддомен фронтенда. Хранить - как секретный ключ:
шифрованным в базе, по одной записи на магазин.

**Права выдаёт только Владелец или Управляющий** магазина. Остальные роли
кнопку увидят, но разрешение выдать не смогут.

## Шаг 1. Регистрация приложения

Приложение регистрируется на странице OAuth-авторизации в личном кабинете
ЮKassa. Там задаются название, описание, ссылка на сайт, способ получения кода
и набор прав. После регистрации выдаются `client_id` и `client_secret`.

Способов получить код два, и выбор влияет на код приложения:

| Способ | Когда подходит |
|---|---|
| Передавать в Callback URL | приложение умеет принимать HTTP-запрос: сайт, CRM, бэкенд бота |
| Показывать на странице | приложение не умеет: Smart TV, десктоп без своего домена, консоль |

## Шаг 2. Ссылка на выдачу прав

```python
from urllib.parse import urlencode

AUTHORIZE_URL = "https://yookassa.ru/oauth/v2/authorize"


def build_authorize_url(client_id: str, state: str) -> str:
    """Ссылка, по которой пользователь выдаёт приложению права."""
    query = urlencode(
        {
            "response_type": "code",
            "client_id": client_id,
            # state возвращается обратно без изменений. Здесь одноразовое
            # значение, привязанное к сессии: по нему на шаге возврата видно,
            # что код пришёл от того же пользователя, который начал выдачу.
            "state": state,
        }
    )
    return f"{AUTHORIZE_URL}?{query}"
```

`state` не формальность. Без него обработчик Callback URL примет код от кого
угодно и привяжет чужой магазин к учётной записи, которая права не выдавала.
Значение должно быть случайным, одноразовым и храниться на стороне приложения
до возврата пользователя.

```python
import secrets

state = secrets.token_urlsafe(32)
save_pending_authorization(user_id=current_user.id, state=state)

url = build_authorize_url(client_id=CLIENT_ID, state=state)
```

## Шаг 3. Код подтверждения

**Через Callback URL.** Пользователь возвращается на адрес, указанный при
регистрации, а код и `state` приезжают в query.

```python
from fastapi import FastAPI, HTTPException, Request

app = FastAPI()


@app.get("/yookassa/callback")
async def yookassa_callback(request: Request):
    code = request.query_params.get("code")
    state = request.query_params.get("state")

    # Одноразовый state: гасим его при первом использовании, иначе повтор
    # ссылки привяжет магазин ещё раз.
    user_id = consume_pending_authorization(state)
    if user_id is None or not code:
        raise HTTPException(status_code=400, detail="Неизвестный state")

    token = await exchange_code_for_token(code)
    await save_shop_token(user_id, token)
    return {"ok": True}
```

**Вводом вручную.** OAuth-сервер показывает код на странице, пользователь
переносит его в приложение. Обработчик тот же, только `code` берётся из формы,
а `state` из текущей сессии.

Код живёт пять минут. Обменивать его нужно сразу, а не по расписанию.

## Шаг 4. Обмен кода на токен

```python
import httpx

TOKEN_URL = "https://yookassa.ru/oauth/v2/token"


async def exchange_code_for_token(code: str) -> str:
    """Обменять код подтверждения на OAuth-токен."""
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            TOKEN_URL,
            # Идентификатор и пароль приложения уходят basic-авторизацией,
            # в теле их быть не должно.
            auth=(CLIENT_ID, CLIENT_SECRET),
            data={"grant_type": "authorization_code", "code": code},
        )

    if response.status_code != 200:
        # Частые причины: код просрочен, уже обменян или выдан другому
        # приложению. Повторять бессмысленно, нужна новая выдача прав.
        raise RuntimeError(f"OAuth-сервер ответил {response.status_code}")

    payload = response.json()
    return payload["access_token"]
```

Ответ выглядит так:

```json
{
  "access_token": "AAEAAAAA8cSwPQAAAXUcZAXZ9hmYP3bKvY2r3ALwPYRYhrnOiKDEou9aLKiLYArHj2Tke-syRshb-1TQ1Ns_nQbc",
  "expires_in": 94607999
}
```

`expires_in` это секунды, примерно пять лет. Дату истечения стоит сохранить
вместе с токеном: по ней видно, у каких магазинов пора запрашивать права
заново, не дожидаясь отказа в момент платежа.

## Шаг 5. Работа от имени магазина

Дальше начинается обычная работа с библиотекой, только вместо `shop_id` и
`secret_key` передаётся токен.

```python
from yookassax import AsyncYooKassa

async with AsyncYooKassa(oauth_token=token) as kassa:
    settings = await kassa.settings.get()
```

Первым делом стоит спросить настройки магазина: от них зависит, что вообще
доступно.

```python
print(settings.account_id)          # идентификатор магазина
print(settings.test)                # True - только тестовые платежи
print(settings.payment_methods)     # какие способы оплаты подключены
print(settings.fiscalization_enabled)
```

У тестового магазина `test` равно `True`, а из способов оплаты доступны только
банковская карта и ЮMoney. Если приложение показывает пользователю список
способов, брать его нужно отсюда, а не из своего представления о ЮKassa.

Платёж создаётся как обычно:

```python
payment = await kassa.payments.create(
    {
        "amount": {"value": "100.00", "currency": "RUB"},
        "confirmation": {
            "type": "redirect",
            "return_url": "https://www.example.com/return_url",
        },
        "capture": True,
        "description": "Заказ №1",
    },
    idempotency_key=f"order-{order_id}",
)
```

Синхронно всё то же самое:

```python
from yookassax import YooKassa

with YooKassa(oauth_token=token) as kassa:
    payment = kassa.payments.create({...})
```

Задать одновременно `oauth_token` и пару `shop_id` с `secret_key` нельзя:
клиент откажется собираться с `ConfigurationError`, чтобы не выбирать за вас,
чьими правами идти в API.

Клиент на магазин лучше создавать один и держать: внутри пул соединений.

```python
class ShopClients:
    """Клиенты по магазинам: один на токен, а не один на запрос."""

    def __init__(self) -> None:
        self._clients: dict[str, AsyncYooKassa] = {}

    def get(self, shop_id: str, token: str) -> AsyncYooKassa:
        client = self._clients.get(shop_id)
        if client is None:
            client = AsyncYooKassa(oauth_token=token)
            self._clients[shop_id] = client
        return client

    async def close(self) -> None:
        for client in self._clients.values():
            await client.aclose()
```

## Уведомления только по API

Партнёрскому приложению личный кабинет недоступен, поэтому подписки создаются
через API - и только OAuth-токеном. С парой `shop_id` и `secret_key` тот же
вызов вернёт 401 `Authentication type is not allowed`.

```python
async with AsyncYooKassa(oauth_token=token) as kassa:
    hook = await kassa.webhooks.add(
        "payment.succeeded", "https://www.example.com/notification_url"
    )
    print(hook.id, hook.event, hook.url)

    for existing in await kassa.webhooks.list():
        print(existing.id, existing.event, existing.url)

    await kassa.webhooks.remove(hook.id)
```

Три вещи, о которые спотыкаются:

**Подписка на событие - отдельный объект.** Нужны и `payment.succeeded`, и
`payment.canceled` - создавайте два.

**Свой набор подписок на каждый токен.** Подписки живут при токене, а не при
приложении: новый магазин - новый набор.

**Приходят только свои объекты.** Уведомления касаются платежей, созданных
вашим приложением, а не всего оборота магазина.

Партнёрскому приложению доступны события платежей, возвратов и привязки
способа оплаты:

```python
from yookassax.webhooks import EVENTS

print(EVENTS)
```

Разбор уведомления не зависит от способа аутентификации, он описан в
[примерах по уведомлениям](13-webhooks.md). Одно уточнение для партнёров:
объект берётся тем же токеном, которым создавался платёж.

```python
notification = webhooks.parse(await request.json())

if notification.is_payment_succeeded:
    kassa = clients.get(shop_id, token_for(shop_id))
    payment = await kassa.payments.get(notification.object.id)
    if payment.is_succeeded:
        ...
```

## Хранение и жизненный цикл токена

Токен живёт пять лет, но перестать работать может раньше: пользователь отозвал
права, приложение удалили, права урезали. ЮKassa сообщает об этом в момент
операции.

```python
from yookassax import Forbidden, Unauthorized

try:
    payment = await kassa.payments.create(params)
except Unauthorized:
    # Токен мёртв: отозван, просрочен или приложение удалено. Повторять
    # нечего, нужна новая выдача прав.
    await mark_shop_disconnected(shop_id)
    raise
except Forbidden:
    # Токен жив, но прав на эту операцию не запрашивали. Лечится изменением
    # набора прав приложения и повторной выдачей, не повтором запроса.
    await mark_scope_missing(shop_id)
    raise
```

Разница важная: `Unauthorized` означает «переподключите магазин»,
`Forbidden` - «приложению не хватает права», и пользователю это надо сказать
по-разному.

## Права приложения

При регистрации выбирается набор прав. Просить больше, чем нужно, - лишний
повод для отказа при выдаче:

| Право | Что открывает в библиотеке |
|---|---|
| создание платежей | `kassa.payments.create` |
| подтверждение платежей | `kassa.payments.capture` |
| просмотр платежей | `kassa.payments.get`, `list`, `iterate` |
| отмена платежей | `kassa.payments.cancel` |
| сохранение способов оплаты | `kassa.payment_methods`, автоплатежи |
| создание возвратов | `kassa.refunds.create` |
| просмотр возвратов | `kassa.refunds.get`, `list`, `iterate` |
| просмотр комиссий | комиссия ЮKassa в объекте платежа |

Права проверяются в момент операции, а не при получении токена. Если набор
изменили после выдачи, старый токен новых прав не получит: нужна повторная
выдача.

## Тестирование

Для отладки нужен тестовый магазин: платежи в нём проходят как настоящие, но
деньги не двигаются, а `test` у объектов равен `True`.

```python
settings = await kassa.settings.get()
assert settings.test is True, "боевой магазин, платежи настоящие"
```

Проверка на старте дешевле разбирательств потом: перепутанные боевой и
тестовый токены выясняются иначе только на первом платеже.

Такой же проверкой защищён живой прогон самой библиотеки: тесты в
`tests/integration` отказываются работать с ключом, который не от тестового
магазина, потому что создают платежи.
