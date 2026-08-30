# The test shop

In a test shop everything behaves like a real payment, but no money moves. It
is the only way to debug an integration without touching real money.

* [Telling a test shop apart](#telling-a-test-shop-apart)
* [What a test shop can do](#what-a-test-shop-can-do)
* [Guarding against live credentials](#guarding-against-live-credentials)
* [A test payment](#a-test-payment)
* [Mocking HTTP in your own tests](#mocking-http-in-your-own-tests)
* [The live run](#the-live-run)

## Telling a test shop apart

By the `GET /me` response and by the `test` field on objects.

```python
settings = kassa.settings.get()

print(settings.test)          # True for a test shop
print(settings.account_id)
print(settings.status)        # enabled
```

A test shop's secret key starts with `test_`, a live one with `live_`. Check
both: the prefix is visible before the first request, and `settings.test`
confirms it from YooKassa's side.

## What a test shop can do

A test shop can do less than a live one, and that is not an integration bug:

```python
print(settings.payment_methods)   # ['yoo_money', 'bank_card']
```

Only bank card and YooMoney are available. Payouts, Safe deal, the SBP bank
directory, personal data and self-employed features need separate enablement
and answer 401 or 403 without it.

Take the payment method list for your interface from
`settings.payment_methods` rather than from your own idea of YooKassa: it
differs from shop to shop.

## Guarding against live credentials

The most expensive mistake in tests is drifting into the live shop by accident.
The guard takes three lines and is worth it.

```python
def build_client(shop_id: str, secret_key: str) -> YooKassa:
    """A client for tests: a live key is refused."""
    if not secret_key.startswith("test_"):
        raise RuntimeError("a test shop key is required: the tests create payments")
    return YooKassa(shop_id=shop_id, secret_key=secret_key)
```

And the same again after the first request, this time from YooKassa's answer:

```python
settings = kassa.settings.get()
assert settings.test is True, "this is a live shop, payments are real"
```

## A test payment

Created like any other. The response has `test` set to `True`:

```python
payment = kassa.payments.create(
    {
        "amount": {"value": "2.00", "currency": "RUB"},
        "confirmation": {
            "type": "redirect",
            "return_url": "https://www.example.com/return_url",
        },
        "capture": True,
        "description": "Order 1",
    }
)

print(payment.test)               # True
print(payment.status)             # pending
print(payment.confirmation_url)   # send the payer here
```

The payment stays `pending` until somebody follows `confirmation_url` and pays
with a test card. Creating it does not complete it, which is why an automated
test for `capture` or `cancel` is impossible without a manual step: without a
payer the payment never reaches `waiting_for_capture`.

## Mocking HTTP in your own tests

Checking your own logic needs no network, and going over one is harmful: tests
become slow and depend on somebody else's uptime. HTTP is mocked with `respx`,
which is how the library's own tests work.

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

The same approach covers branches a live shop will not reproduce: cancellation,
capture, 429 and 500 errors, a dropped connection.

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

## The live run

The library has a separate set of tests that goes to the real API. Without
credentials it is skipped entirely, so an ordinary run and CI never notice it.

```bash
export YOOKASSA_SHOP_ID=... YOOKASSA_SECRET_KEY=test_...
pytest tests/integration
```

The key test there is `test_real_responses_have_no_unknown_fields`: it parses
real responses from the shop and requires every field to have a place in the
models. The point is that the OpenAPI specification lags behind the API - that
is exactly how the `protocol`, `method_completed` and `challenge_completed`
fields of 3-D Secure were found, none of which the specification mentions.

The same trick is useful in your own application: parse real responses from
time to time and watch for `UnknownFieldWarning`. Details in the
[errors guide](14-errors.md#fields-the-model-does-not-know).
