# HTTP response codes

What each YooKassa code means, what the library turns it into and what to do
about it. The exception hierarchy and retry settings are in the
[errors guide](14-errors.md).

* [The table](#the-table)
* [200 and the pending status](#200-and-the-pending-status)
* [400: a malformed request](#400-a-malformed-request)
* [401: authentication](#401-authentication)
* [403: not enough rights](#403-not-enough-rights)
* [404: no such object](#404-no-such-object)
* [405 and 415](#405-and-415)
* [429: too often](#429-too-often)
* [500: the result is unknown](#500-the-result-is-unknown)
* [About the idempotency key on errors](#about-the-idempotency-key-on-errors)

## The table

| Code | Error code | Exception | Retried automatically |
|---|---|---|---|
| 200 | — | none, an object comes back | — |
| 400 | `invalid_request` | `BadRequest` | no |
| 401 | `invalid_credentials` | `Unauthorized` | no |
| 403 | `forbidden` | `Forbidden` | no |
| 404 | `not_found` | `NotFound` | no |
| 405 | — | `APIError` | no |
| 415 | — | `APIError` | no |
| 429 | `too_many_requests` | `RateLimited` | yes |
| 500 | `internal_server_error` | `ServerError` | yes |
| 202 | — | `ResponseProcessing` | yes |
| no response | — | `TransportError` | yes |

## 200 and the pending status

A successful response does not mean the operation is finished. A payment comes
back in the `pending` status until the payer confirms it.

```python
payment = kassa.payments.create(params)

payment.is_pending             # waiting for the payer
payment.is_waiting_for_capture # funds are held
payment.is_succeeded           # the money is with the shop
payment.is_canceled            # the money is with the payer
```

There are two ways to learn about a status change, and the first is the right
one:

**A notification.** Subscribe to `payment.succeeded`; the handler is in the
[notifications guide](13-webhooks.md).

**Polling.** If notifications are unavailable, repeat `get` with a growing
interval. Polling in a tight loop runs into 429.

```python
import time

def wait_for_final_status(kassa, payment_id, attempts=10):
    """Wait for a final status, growing the pause by Fibonacci."""
    previous, delay = 1, 1
    for _ in range(attempts):
        payment = kassa.payments.get(payment_id)
        if not payment.is_pending:
            return payment
        time.sleep(delay)
        previous, delay = delay, previous + delay
    return None
```

An object stuck in `pending` past its confirmation window is a reason to
contact YooKassa support, not to keep polling.

## 400: a malformed request

The syntax or the logic is wrong: a required parameter is missing, a value has
the wrong format, mutually exclusive fields were sent, or something is off with
the idempotency key.

```python
from yookassax import BadRequest

try:
    payment = kassa.payments.create(params)
except BadRequest as error:
    logger.error(
        "YooKassa rejected the request: %s, field %s, request_id %s",
        error.description,
        error.parameter,
        error.request_id,
    )
```

Retrying is pointless: the same request gives the same answer, and the library
does not retry these. It is fixed in the code, not at runtime.

`parameter` names the field that caused the rejection - that is where to start.

## 401: authentication

The credentials were not accepted. The cause depends on the method.

**HTTP Basic (your own shop).** The identifier or key is missing, they are
swapped, the key is stale, or the identifier belongs to another shop.

**OAuth (a partner application).** The token was not sent, expired, was revoked
by the user, or the application it was issued for was deleted.

```python
from yookassax import Unauthorized

try:
    settings = kassa.settings.get()
except Unauthorized:
    # For a partner application this means "reconnect the shop",
    # for your own it means "check the credentials".
    ...
```

Check credentials at application startup rather than on the first payment:

```python
settings = kassa.settings.get()
logger.info("shop %s, test: %s", settings.account_id, settings.test)
```

## 403: not enough rights

The request is valid but the operation is not allowed for this shop. Typical
cases: recurring payments are not enabled, card data is sent without a PCI DSS
certificate, or - for OAuth - the permission was never requested when the
application was registered.

```python
from yookassax import Forbidden

try:
    payment = kassa.payments.create({**params, "payment_method_id": saved_method_id})
except Forbidden as error:
    logger.error("The shop is not allowed to do this: %s", error.description)
```

The error is permanent: it is fixed through shop settings or the application's
permissions, not by retrying.

## 404: no such object

The object does not exist, or it belongs to a different shop. The second is
more common than it seems: live credentials with a payment id from the test
shop, for example.

```python
from yookassax import NotFound

try:
    payment = kassa.payments.get(payment_id)
except NotFound:
    ...
```

Sometimes a 404 arrives for an object you have just created - the request hit a
replica. Retrying after a second helps, but more often the identifier simply
came from the wrong place.

## 405 and 415

`405` is a wrong HTTP method, `415` a wrong `Content-Type`. Through the library
they do not appear: it builds both the method and the headers itself.

You can only meet them on your own call to an undescribed endpoint:

```python
from yookassax import Operation

operation = Operation(method="GET", path="/payments/{id}/cancel")   # wrong
```

Cancelling a payment is a POST. The library sends what you asked for, and
YooKassa answers 405.

## 429: too often

The request rate was exceeded. The library retries such a request itself, with
exponential backoff and jitter - jitter is there so a batch of clients that all
got a 429 does not go for a second round at the same time.

```python
kassa = YooKassa(shop_id="...", secret_key="...", retries=5)
```

If 429 keeps coming, retries will not help: the rate has to come down. The
usual cause is polling statuses in a tight loop instead of using notifications.

## 500: the result is unknown

A failure on the YooKassa side. The important part: **a 500 does not mean the
operation failed**. The payment may have been created while the response was
lost.

The library retries with the same idempotency key, so a retry does not create a
second payment. If the attempts run out, find out the state rather than
creating it again.

```python
from yookassax import ServerError, TransportError

key = f"order-{order_id}"

try:
    payment = kassa.payments.create(params, idempotency_key=key)
except (ServerError, TransportError):
    # The same key: if the payment exists, it comes back.
    payment = kassa.payments.create(params, idempotency_key=key)
```

If 500 persists for more than half an hour, that is a support request with the
`request_id`, not an endless retry.

## About the idempotency key on errors

There is one rule, and it goes against intuition:

**Fixed the request - use a new key.** After 400, 403, 404, 405 and 415 the
request changes, so the key must change too. The old key is bound to the old
body, and YooKassa may return the previous result.

**Repeating the same request - use the same key.** After 500, 429 and a
connection failure the body did not change, and repeating with the same key is
what protects you from a second payment.

The library sets the key itself and reuses it across its own retries. Your own
key is needed when your code may retry - build it from the order identifier
rather than at random:

```python
kassa.payments.create(params, idempotency_key=f"order-{order_id}")
```

A random key differs on retry, and the protection against a double payment
stops working.
