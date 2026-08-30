# Client setup

* [Authentication](#authentication)
* [Client options](#client-options)
* [Closing connections](#closing-connections)
* [The client and the event loop](#the-client-and-the-event-loop)
* [Shop information](#shop-information)
* [Managing notification subscriptions](#managing-notification-subscriptions)
* [Several shops in one process](#several-shops-in-one-process)

## Authentication

Your own shop: an identifier and a secret key.

```python
from yookassax import YooKassa

kassa = YooKassa(shop_id="123456", secret_key="live_...")
```

The asynchronous client takes the same arguments:

```python
from yookassax import AsyncYooKassa

kassa = AsyncYooKassa(shop_id="123456", secret_key="live_...")
```

Someone else's shop: an OAuth token that the shop issued to your application.

```python
kassa = YooKassa(oauth_token="token")
```

You cannot pass both at once; the client refuses to be built:

```python
from yookassax import ConfigurationError

try:
    YooKassa(shop_id="123456", secret_key="live_...", oauth_token="token")
except ConfigurationError as error:
    print(error)
```

A configuration error is raised when the client is created, not on the first
payment. That way wrong credentials surface at application startup.

## Client options

```python
kassa = YooKassa(
    shop_id="123456",
    secret_key="live_...",
    timeout=30.0,   # single request timeout, seconds
    retries=3,      # total attempts including the first one
    api_url="https://api.yookassa.ru/v3",
)
```

`retries=1` disables retries. See the [errors guide](14-errors.md) for what
exactly gets retried.

## Closing connections

The client holds a connection pool, so create it once per application rather
than per request.

```python
with YooKassa(shop_id="123456", secret_key="live_...") as kassa:
    ...
```

```python
async with AsyncYooKassa(shop_id="123456", secret_key="live_...") as kassa:
    ...
```

Without a context manager, close explicitly: `kassa.close()` for the
synchronous client, `await kassa.aclose()` for the asynchronous one.

In a web application it is convenient to keep a single client for the whole
process lifetime. A FastAPI example:

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

## The client and the event loop

The asynchronous client holds a connection pool, and the pool is bound to the
event loop it was opened in: the sockets live in that loop's transports. Reusing
a client in another loop does not work - the first request fails with
`RuntimeError: Event loop is closed`.

In an ordinary application this never shows: there is one loop for the life of
the process. But Celery runs every task through `asyncio.run`, that is in a loop
of its own, which it then closes.

```python
# Wrong: the client outlives the first task's loop.
_client = AsyncYooKassa(oauth_token=token)


@celery_app.task
def charge():
    asyncio.run(_charge())          # the second call fails
```

The client must not outlive the loop:

```python
@celery_app.task
def charge():
    asyncio.run(_charge())


async def _charge():
    async with AsyncYooKassa(oauth_token=token) as kassa:
        await kassa.payments.create({...})
```

If clients are cached (one per shop, say), the cache has to be keyed by loop and
closed before that loop goes away:

```python
loop = asyncio.get_running_loop()
client = cache.setdefault(loop, {}).get(token)
```

None of this applies to the synchronous client: it has no event loop.

## Shop information

```python
me = kassa.settings.get()

print(me.account_id)          # shop identifier
print(me.test)                # True for a test shop
print(me.payment_methods)     # available payment methods
print(me.fiscalization)       # fiscalization settings
```

```python
me = await kassa.settings.get()
```

Calling this at startup is useful: it immediately shows whether live or test
credentials are wired up. Otherwise you find out on the first payment.

## Managing notification subscriptions

Subscription management works with an OAuth token only. A shop secret key
cannot perform these requests.

```python
kassa = YooKassa(oauth_token="token")

kassa.webhooks.add("payment.succeeded", "https://merchant-site.com/webhook")
kassa.webhooks.add("refund.succeeded", "https://merchant-site.com/webhook")

for webhook in kassa.webhooks.list():
    print(webhook.id, webhook.event, webhook.url)

kassa.webhooks.remove("wh-1da5c0de")
```

Asynchronously:

```python
await kassa.webhooks.add("payment.succeeded", "https://merchant-site.com/webhook")
page = await kassa.webhooks.list()
await kassa.webhooks.remove("wh-1da5c0de")
```

Parsing the notifications themselves is covered separately in the
[webhooks guide](13-webhooks.md).

## Several shops in one process

Credentials belong to the client instance, so shops do not interfere with each
other.

```python
shops = {
    "first": YooKassa(shop_id="111", secret_key="live_a..."),
    "second": YooKassa(shop_id="222", secret_key="live_b..."),
}

payment = shops["first"].payments.create({...})
```

This is an important difference from the official SDK, where credentials live
in `Configuration` at class level. With concurrent payments two requests can
overwrite each other's token, and a payment then goes through the wrong shop.
