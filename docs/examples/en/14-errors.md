# Errors and retries

* [Exception hierarchy](#exception-hierarchy)
* [Inspecting an error](#inspecting-an-error)
* [What gets retried automatically](#what-gets-retried-automatically)
* [Connection failure while creating a payment](#connection-failure-while-creating-a-payment)
* [Tuning retries](#tuning-retries)
* [Fields the model does not know](#fields-the-model-does-not-know)
* [Common errors](#common-errors)

## Exception hierarchy

```
YooKassaError                the base class, catch it when details do not matter
    ConfigurationError       the client was built incorrectly
    TransportError           there was no response at all
    APIError                 the API answered with an error
        BadRequest           400
        Unauthorized         401
        Forbidden            403
        NotFound             404
        Gone                 410
        RateLimited          429
        ResponseProcessing   202
        ServerError          500
```

```python
from yookassax import (
    BadRequest,
    Forbidden,
    NotFound,
    TransportError,
    YooKassaError,
)

try:
    payment = kassa.payments.create({...})
except Forbidden:
    ...
except BadRequest as error:
    ...
except TransportError:
    ...
except YooKassaError:
    ...
```

## Inspecting an error

Every API error carries the parsed response body.

```python
from yookassax import APIError

try:
    payment = kassa.payments.create({"amount": {"value": "0.00", "currency": "RUB"}})
except APIError as error:
    print(error.status)        # 400
    print(error.code)          # invalid_request
    print(error.description)   # Amount is below the minimum
    print(error.parameter)     # amount
    print(error.request_id)    # request identifier for support
    print(error.payload)       # the whole response body
```

It is worth logging `request_id`: YooKassa support can look the request up by
it.

## What gets retried automatically

The client retries what is likely to succeed on a second attempt:

| Code | Meaning | Retried |
|---|---|---|
| 202 | accepted, still processing | yes |
| 429 | request rate exceeded | yes |
| 500 | failure on the YooKassa side | yes |
| connection failure | no response arrived | yes |
| 400 | malformed request | no |
| 401 | wrong credentials | no |
| 403 | operation not allowed | no |
| 404 | object does not exist | no |

Request errors are deliberately not retried: an identical second request gives
an identical answer, and on payment paths extra attempts only get in the way.

The pause between attempts grows exponentially and jitters slightly. Jitter is
there so that a batch of clients that all received a 429 does not go for a
second round at the same time.

## Connection failure while creating a payment

`TransportError` is a separate type for a reason. If creating a payment failed
with it, **it is unknown whether the payment was created**: the request may
have reached YooKassa while the response was lost.

The client retries with the same idempotency key, so no second payment appears.
But if the attempts run out, the state remains unclear.

The right reaction is not to blindly create the payment again, but to find out
the state.

```python
from yookassax import TransportError

idempotency_key = f"order-{order_id}"

try:
    payment = kassa.payments.create(params, idempotency_key=idempotency_key)
except TransportError:
    # Retry with the SAME key: if the payment already exists,
    # YooKassa returns it instead of creating a second one.
    payment = kassa.payments.create(params, idempotency_key=idempotency_key)
```

This is exactly why an idempotency key should be derived from the order
identifier rather than left random: a random key would differ on retry.

## Tuning retries

```python
kassa = YooKassa(
    shop_id="123456",
    secret_key="live_...",
    retries=5,      # total attempts including the first one
    timeout=10.0,   # single request timeout
)
```

`retries=1` disables retries entirely.

For background jobs it makes sense to raise the number of attempts; for a web
request handler, to lower it: the user should not wait through three rounds of
backoff.

## Fields the model does not know

YooKassa adds fields to responses silently. Parsing does not break because of
it: anything extra stays in `raw` and is reachable through `extra()`. But there
would be no other way to find out, so the library warns.

```python
payment = kassa.payments.get(payment_id)
# UnknownFieldWarning: Payment: в ответе API есть поля, которых нет в модели:
# loyalty_bonus. Значения доступны через extra(), но, возможно, стоит обновить
# yookassax.

payment.extra("loyalty_bonus")   # the value is already available
```

The message reads: the Payment model got a field it does not know,
`loyalty_bonus`; the value is available through `extra()`, and the library is
worth updating. Runtime messages are in Russian throughout the library,
exception texts included.

The warning points at a line of your own code rather than at the library
internals: it shows which request brought the new field in.

**There will be no spam.** Each model-and-field pair is reported once per
process lifetime: a page of a hundred payments carrying a new field produces
one line, not a hundred.

This is a warning, not an error: nothing breaks and nothing has to be done. The
sensible reaction is to look at what appeared and update `yookassax` when the
field is needed.

It is silenced with the standard filter:

```python
import warnings
from yookassax import UnknownFieldWarning

warnings.filterwarnings("ignore", category=UnknownFieldWarning)
```

The opposite works too: in tests the warning can be turned into an error so
that a change in the API response does not go unnoticed.

```python
warnings.filterwarnings("error", category=UnknownFieldWarning)
```

If logs are collected through `logging`, warnings are easy to route there:

```python
import logging

logging.captureWarnings(True)
```

## Common errors

**403 when saving a payment method or charging it.** Recurring payments are not
enabled for the shop. The error is permanent, retrying is pointless, contact
YooKassa.

```python
except Forbidden as error:
    logger.error("Recurring payments are not enabled: %s", error.description)
```

**401 on every request.** Wrong credentials: a shop secret key where an OAuth
token is required, or the other way round. Verify with `kassa.settings.get()`
at startup.

**400 with a parameter in the response.** Check which field was rejected:

```python
except BadRequest as error:
    logger.error("Field %s: %s", error.parameter, error.description)
```

**404 for an object you have just created.** Happens when a replica is queried
right after a write. Retrying after a second helps, but more often it means the
identifier came from the wrong place.
