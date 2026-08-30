# Examples

[Русский](../ru/README.md) | English, [back to the library overview](../../../README.en.md)

Examples for yookassax, an unofficial library: the project is not affiliated
with YooKassa or YooMoney and is not supported by them.

Every scenario is shown in both modes: synchronous and asynchronous. The only
difference between them is `await`; the method sets are identical.

| File | Topic |
|---|---|
| [01-configuration.md](01-configuration.md) | Client setup, authentication, shop info, subscriptions |
| [02-payments.md](02-payments.md) | Payments: create, capture, cancel, list |
| [03-refunds.md](03-refunds.md) | Refunds, including partial ones |
| [04-receipts.md](04-receipts.md) | Receipts (Russian federal law 54-FZ) |
| [05-deals.md](05-deals.md) | Safe deals |
| [06-payouts.md](06-payouts.md) | Payouts to cards, SBP, wallets, self-employed |
| [07-self-employed.md](07-self-employed.md) | Self-employed registration |
| [08-personal-data.md](08-personal-data.md) | Recipient personal data |
| [09-sbp-banks.md](09-sbp-banks.md) | SBP bank directory |
| [10-invoices.md](10-invoices.md) | Invoices |
| [11-payment-methods.md](11-payment-methods.md) | Saved payment methods, subscriptions |
| [12-pos-links.md](12-pos-links.md) | POS links |
| [13-webhooks.md](13-webhooks.md) | Incoming notifications: FastAPI, Django, Flask |
| [14-errors.md](14-errors.md) | Errors, retries, idempotency |

All examples assume the client is already created:

```python
from yookassax import YooKassa

kassa = YooKassa(shop_id="123456", secret_key="live_...")
```

or, for the asynchronous mode:

```python
from yookassax import AsyncYooKassa

kassa = AsyncYooKassa(shop_id="123456", secret_key="live_...")
```

## About builders

The official SDK ships a builder class for every request, such as
`PaymentRequestBuilder`. This library has none: a request body is a plain
dictionary.

The reason is that a builder mirrors the JSON structure but lags behind it.
When YooKassa adds a field, a dictionary accepts it immediately, while a
builder only does so after the library is updated. Writing a dictionary
straight from the API documentation is simpler than hunting for the right
setter.

If you need validation before sending, build your own model on the application
side and pass `model_dump()`.
