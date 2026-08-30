# yookassax

[Русский](README.md) | English

A [YooKassa](https://yookassa.ru/developers/api) client for Python in two modes:
synchronous and asynchronous. Typed models, notification parsing, idempotency
and retries out of the box.

```bash
pip install yookassax
```

Requires Python 3.10 or newer. The only dependency is `httpx`.

## Quick start

Synchronously:

```python
from yookassax import YooKassa

with YooKassa(shop_id="123456", secret_key="live_...") as kassa:
    payment = kassa.payments.create({
        "amount": {"value": "100.00", "currency": "RUB"},
        "confirmation": {"type": "redirect", "return_url": "https://example.com/done"},
        "capture": True,
        "description": "Order 42",
    })
    print(payment.confirmation_url)
```

Asynchronously, the same thing:

```python
from yookassax import AsyncYooKassa

async with AsyncYooKassa(shop_id="123456", secret_key="live_...") as kassa:
    payment = await kassa.payments.create({
        "amount": {"value": "100.00", "currency": "RUB"},
        "confirmation": {"type": "redirect", "return_url": "https://example.com/done"},
        "capture": True,
    })
```

Both modes expose the same set of methods, and a test keeps it that way. Moving
from one to the other comes down to adding `await`.

## Examples

Every scenario from the official documentation, both modes, two languages:
[English](docs/examples/en/README.md),
[русский](docs/examples/ru/README.md).

| | |
|---|---|
| [Client configuration](docs/examples/en/01-configuration.md) | authentication, shop, subscriptions |
| [Payments](docs/examples/en/02-payments.md) | create, capture, cancel, list |
| [Refunds](docs/examples/en/03-refunds.md) | full and partial |
| [Receipts](docs/examples/en/04-receipts.md) | fiscalization, marked goods |
| [Deals](docs/examples/en/05-deals.md) | safe deal end to end |
| [Payouts](docs/examples/en/06-payouts.md) | card, SBP, wallet, self-employed |
| [Self-employed](docs/examples/en/07-self-employed.md) | registration and confirmation |
| [Personal data](docs/examples/en/08-personal-data.md) | payout recipients |
| [SBP banks](docs/examples/en/09-sbp-banks.md) | directory |
| [Invoices](docs/examples/en/10-invoices.md) | payment link |
| [Payment methods](docs/examples/en/11-payment-methods.md) | subscriptions and recurring charges |
| [POS links](docs/examples/en/12-pos-links.md) | static QR codes |
| [Notifications](docs/examples/en/13-webhooks.md) | FastAPI, Django, Flask |
| [Errors and retries](docs/examples/en/14-errors.md) | idempotency, connection failures |

## How this differs from the official SDK

**Credentials live on the client instance.** The official SDK keeps them in
`Configuration` at class level. If an application serves several shops from one
process, two payments can overwrite each other's token between configuration and
call, and a payment goes out through the wrong shop. Here every client carries
its own credentials, so that race does not exist.

**The asynchronous mode is real.** The official SDK is synchronous, `requests`
underneath. Calling it from an async handler stalls the whole worker: while the
API call is in flight, the process serves nobody.

**The idempotency key is set automatically** on every mutating request. A retry
after a connection failure goes out with the same key, so no second payment
appears.

**Retries** on 202, 429 and 500 with exponential backoff and jitter. Request
errors (400, 404) are not retried: an identical second request gives an
identical answer.

**Models are typed and tolerant of new fields.** YooKassa adds fields to
responses; a strict model would turn that into a refusal to serve payments.
Anything unknown is kept in `raw` and reachable through `extra`. Not silently
though: every such field raises `UnknownFieldWarning` once, otherwise nobody
would learn about it at all.

**No builders.** The request body is a plain dictionary: it accepts new API
fields immediately, not after a library release.

## Working with payments

```python
payment = kassa.payments.create({...})

payment.is_pending             # waiting for the payer
payment.is_waiting_for_capture # funds held, capture or cancel required
payment.is_succeeded           # the money is with the shop
payment.is_canceled            # the money is with the payer

payment.amount.value           # Decimal("100.00"), not float
payment.created_at             # timezone aware datetime
payment.confirmation_url       # where to send the payer, or None

kassa.payments.capture(payment.id)
kassa.payments.cancel(payment.id)
```

## Lists

```python
page = kassa.payments.list(status="succeeded", limit=50)
for payment in page:
    print(payment.id)

if page.has_more:
    next_page = kassa.payments.list(status="succeeded", cursor=page.next_cursor)
```

Or without paging by hand:

```python
for payment in kassa.payments.iterate(status="succeeded"):
    print(payment.id)
```

In asynchronous mode the same thing through `async for`.

## Notifications

YooKassa does not sign the notification body, so the only built-in check is the
sender address. It is not enough: make money decisions from the API response,
not from the notification body.

```python
from fastapi import Request, Response
from yookassax import webhooks

@app.post("/webhook")
async def handle(request: Request):
    if not webhooks.is_trusted_ip(request.headers.get("X-Real-IP", "")):
        return Response(status_code=403)

    notification = webhooks.parse(await request.json())

    if notification.is_payment_succeeded:
        payment = await kassa.payments.get(notification.object.id)
        if payment.is_succeeded:
            ...

    return {"ok": True}
```

Use a trustworthy sender address. Behind a reverse proxy that is the one the
proxy sets itself, usually `X-Real-IP` from nginx. The leftmost
`X-Forwarded-For` element is supplied by the client, which makes the check
meaningless.

Answer 200 quickly: otherwise YooKassa repeats the delivery and the handler
receives the same event again.

## Errors

```python
from yookassax import BadRequest, Forbidden, TransportError, YooKassaError

try:
    payment = kassa.payments.create({...})
except Forbidden:
    # the shop is not allowed to do this, commonly: recurring payments are off
    ...
except BadRequest as error:
    print(error.code, error.description, error.parameter)
except TransportError:
    # there was no response at all, the payment state is unknown
    ...
except YooKassaError:
    ...
```

`TransportError` sits apart from the rest on purpose: if creating a payment
failed with it, it is unknown whether the payment was created.

## New fields in responses

A field the model does not have breaks nothing, and it is not hidden either:

```python
payment = kassa.payments.get(payment_id)
# UnknownFieldWarning: Payment: в ответе API есть поля, которых нет в модели:
# loyalty_bonus. Значения доступны через extra(), но, возможно, стоит обновить
# yookassax.

payment.extra("loyalty_bonus")
```

The warning points at a line of your own code and is raised once per
model-and-field pair for the lifetime of the process: a page of a hundred
payments produces one line, not a hundred. It is silenced with the standard
filter:

```python
import warnings
from yookassax import UnknownFieldWarning

warnings.filterwarnings("ignore", category=UnknownFieldWarning)
```

## Available resources

`payments`, `refunds`, `receipts`, `payouts`, `webhooks`, `settings`,
`payment_methods`, `deals`, `invoices`, `personal_data`, `self_employed`,
`pos_links`, `sbp_banks`.

Every route of the official OpenAPI specification is covered. A test keeps that
coverage honest.

## OAuth

For working with other people's shops:

```python
kassa = YooKassa(oauth_token="the token the shop issued")
```

It cannot be combined with `shop_id` and `secret_key`: the client refuses to be
built rather than choose for you.

## An endpoint the library does not have yet

```python
from yookassax import Operation

operation = Operation(
    method="POST",
    path="/new_endpoint",
    body={"key": "value"},
    idempotent=True,
)
result = kassa.send(operation)
```

## For AI assistants

The `docs` directory holds [`llms.en.txt`](docs/llms.en.txt): a complete
reference to the library in a single file, ready to paste into a model's
context. The Russian version is [`llms.txt`](docs/llms.txt).

## Development

```bash
pip install -e ".[dev]"
pytest
ruff check .
mypy src
```

## License

MIT.
