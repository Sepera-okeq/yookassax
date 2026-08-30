# Partner programme and OAuth

The partner API lets an application (a CRM, a CMS, a bot) work with YooKassa on
behalf of someone else's shop without knowing its secret key. The shop issues
the application an OAuth token, and the application makes payments and refunds.

* [What to know before starting](#what-to-know-before-starting)
* [Step 1. Registering the application](#step-1-registering-the-application)
* [Step 2. The authorization link](#step-2-the-authorization-link)
* [Step 3. The confirmation code](#step-3-the-confirmation-code)
* [Step 4. Exchanging the code for a token](#step-4-exchanging-the-code-for-a-token)
* [Step 5. Working on behalf of the shop](#step-5-working-on-behalf-of-the-shop)
* [Notifications through the API only](#notifications-through-the-api-only)
* [Storing a token and its lifetime](#storing-a-token-and-its-lifetime)
* [Application permissions](#application-permissions)
* [Testing](#testing)

## What to know before starting

**The library works with a ready token.** Exchanging the code for a token
happens on the YooKassa OAuth server (`https://yookassa.ru/oauth/v2/`), not in
the `/v3` API, so it is done here directly with `httpx` - already a dependency
of `yookassax`, nothing extra to install.

**The token can move someone else's money.** It must not go into a cookie, a
log, a repository or a frontend subdomain. Store it like a secret key:
encrypted in the database, one record per shop.

**Only an Owner or a Manager can grant permissions.** Other roles will see the
button but cannot complete the grant.

## Step 1. Registering the application

The application is registered on the OAuth authorization page in the YooKassa
dashboard. There you set the name, the description, the site link, how the code
is delivered and the set of permissions. Registration gives you a `client_id`
and a `client_secret`.

There are two ways to receive the code, and the choice affects your code:

| Way | When it fits |
|---|---|
| Deliver to a Callback URL | the application can receive an HTTP request: a site, a CRM, a bot backend |
| Show on the page | the application cannot: Smart TV, a desktop app without a domain, a console tool |

## Step 2. The authorization link

```python
from urllib.parse import urlencode

AUTHORIZE_URL = "https://yookassa.ru/oauth/v2/authorize"


def build_authorize_url(client_id: str, state: str) -> str:
    """The link where the user grants the application its permissions."""
    query = urlencode(
        {
            "response_type": "code",
            "client_id": client_id,
            # state comes back unchanged. Here it is a one-time value tied to
            # the session: on return it proves the code belongs to the same
            # user who started the grant.
            "state": state,
        }
    )
    return f"{AUTHORIZE_URL}?{query}"
```

`state` is not a formality. Without it the callback handler accepts a code from
anyone and links a stranger's shop to an account that never granted anything.
The value must be random, single-use and stored on your side until the user
comes back.

```python
import secrets

state = secrets.token_urlsafe(32)
save_pending_authorization(user_id=current_user.id, state=state)

url = build_authorize_url(client_id=CLIENT_ID, state=state)
```

## Step 3. The confirmation code

**Through a Callback URL.** The user returns to the address given at
registration, with the code and `state` in the query.

```python
from fastapi import FastAPI, HTTPException, Request

app = FastAPI()


@app.get("/yookassa/callback")
async def yookassa_callback(request: Request):
    code = request.query_params.get("code")
    state = request.query_params.get("state")

    # A single-use state: burn it on first use, otherwise replaying the link
    # links the shop a second time.
    user_id = consume_pending_authorization(state)
    if user_id is None or not code:
        raise HTTPException(status_code=400, detail="Unknown state")

    token = await exchange_code_for_token(code)
    await save_shop_token(user_id, token)
    return {"ok": True}
```

**Typed in by hand.** The OAuth server shows the code on the page and the user
copies it into your application. The handler is the same; `code` comes from a
form and `state` from the current session.

The code lives for five minutes. Exchange it right away, not on a schedule.

## Step 4. Exchanging the code for a token

```python
import httpx

TOKEN_URL = "https://yookassa.ru/oauth/v2/token"


async def exchange_code_for_token(code: str) -> str:
    """Exchange the confirmation code for an OAuth token."""
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            TOKEN_URL,
            # The application id and password go as basic auth; they must not
            # be in the body.
            auth=(CLIENT_ID, CLIENT_SECRET),
            data={"grant_type": "authorization_code", "code": code},
        )

    if response.status_code != 200:
        # Common causes: the code expired, was already exchanged, or belongs to
        # another application. Retrying is pointless, a new grant is needed.
        raise RuntimeError(f"the OAuth server answered {response.status_code}")

    payload = response.json()
    return payload["access_token"]
```

The response looks like this:

```json
{
  "access_token": "AAEAAAAA8cSwPQAAAXUcZAXZ9hmYP3bKvY2r3ALwPYRYhrnOiKDEou9aLKiLYArHj2Tke-syRshb-1TQ1Ns_nQbc",
  "expires_in": 94607999
}
```

`expires_in` is in seconds, about five years. Store the expiry date next to the
token: it shows which shops need a fresh grant before a payment fails.

## Step 5. Working on behalf of the shop

From here it is ordinary work with the library, except the token replaces
`shop_id` and `secret_key`.

```python
from yookassax import AsyncYooKassa

async with AsyncYooKassa(oauth_token=token) as kassa:
    settings = await kassa.settings.get()
```

Ask for the shop settings first: they decide what is available at all.

```python
print(settings.account_id)          # the shop identifier
print(settings.test)                # True - test payments only
print(settings.payment_methods)     # which payment methods are enabled
print(settings.fiscalization_enabled)
```

A test shop has `test` set to `True` and offers only bank card and YooMoney. If
your application shows a list of payment methods, take it from here rather than
from your own idea of what YooKassa supports.

Creating a payment is unchanged:

```python
payment = await kassa.payments.create(
    {
        "amount": {"value": "100.00", "currency": "RUB"},
        "confirmation": {
            "type": "redirect",
            "return_url": "https://www.example.com/return_url",
        },
        "capture": True,
        "description": "Order 1",
    },
    idempotency_key=f"order-{order_id}",
)
```

Synchronously, all the same:

```python
from yookassax import YooKassa

with YooKassa(oauth_token=token) as kassa:
    payment = kassa.payments.create({...})
```

`oauth_token` cannot be combined with `shop_id` and `secret_key`: the client
refuses to be built with a `ConfigurationError` rather than choose whose
credentials to use.

Keep one client per shop instead of one per request: it holds a connection
pool.

```python
class ShopClients:
    """Clients by shop: one per token, not one per request."""

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

## Notifications through the API only

A partner application has no access to the dashboard, so subscriptions are
created through the API - and only with an OAuth token. With a `shop_id` and
`secret_key` pair the same call answers 401 `Authentication type is not
allowed`.

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

Three things people trip over:

**A subscription is one object per event.** If you need both
`payment.succeeded` and `payment.canceled`, create two.

**Each token gets its own set of subscriptions.** They belong to the token, not
to the application: a new shop means a new set.

**Only your own objects arrive.** Notifications cover payments created by your
application, not the whole turnover of the shop.

A partner application can subscribe to payment, refund and payment method
events:

```python
from yookassax.webhooks import EVENTS

print(EVENTS)
```

Parsing a notification does not depend on the authentication method and is
covered in the [notifications guide](13-webhooks.md). One detail for partners:
fetch the object with the same token that created the payment.

```python
notification = webhooks.parse(await request.json())

if notification.is_payment_succeeded:
    kassa = clients.get(shop_id, token_for(shop_id))
    payment = await kassa.payments.get(notification.object.id)
    if payment.is_succeeded:
        ...
```

## Storing a token and its lifetime

A token lives five years but can stop working earlier: the user revoked the
grant, the application was deleted, the permissions were narrowed. YooKassa
tells you at the moment of the operation.

```python
from yookassax import Forbidden, Unauthorized

try:
    payment = await kassa.payments.create(params)
except Unauthorized:
    # The token is dead: revoked, expired, or the application is gone. Nothing
    # to retry, a new grant is needed.
    await mark_shop_disconnected(shop_id)
    raise
except Forbidden:
    # The token is alive but this permission was never requested. Fixed by
    # changing the application's permissions and granting again, not by a retry.
    await mark_scope_missing(shop_id)
    raise
```

The difference matters: `Unauthorized` means "reconnect the shop", `Forbidden`
means "the application lacks a permission", and the user has to be told
different things.

## Application permissions

Registration asks for a set of permissions. Asking for more than you need is
one more reason for a user to decline:

| Permission | What it unlocks in the library |
|---|---|
| create payments | `kassa.payments.create` |
| capture payments | `kassa.payments.capture` |
| view payments | `kassa.payments.get`, `list`, `iterate` |
| cancel payments | `kassa.payments.cancel` |
| save payment methods | `kassa.payment_methods`, recurring charges |
| create refunds | `kassa.refunds.create` |
| view refunds | `kassa.refunds.get`, `list`, `iterate` |
| view commissions | the YooKassa fee inside the payment object |

Permissions are checked at the moment of the operation, not when the token is
issued. If the set changed after the grant, the old token does not gain the new
permissions: the user has to grant again.

## Testing

Debugging needs a test shop: payments there behave like real ones but no money
moves, and objects come back with `test` set to `True`.

```python
settings = await kassa.settings.get()
assert settings.test is True, "this is a live shop, payments are real"
```

Checking at startup is cheaper than finding out later: mixed-up live and test
tokens otherwise surface on the first payment.

The library's own live run is protected the same way: the tests in
`tests/integration` refuse a key that is not from a test shop, because they
create payments.
