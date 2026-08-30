# Logs

The library writes every API call through the standard `logging` module to the
`yookassax` logger. It does not impose a logger of its own: loguru applications
pick these records up with their intercept handler, `logging` applications get
them as usual.

* [Turning it on](#turning-it-on)
* [What gets logged](#what-gets-logged)
* [loguru](#loguru)
* [What never gets logged](#what-never-gets-logged)
* [Structured logs](#structured-logs)

## Turning it on

The logger has no handler by default, so it writes only where logging is
configured:

```python
import logging

logging.basicConfig(level=logging.INFO)
logging.getLogger("yookassax").setLevel(logging.INFO)
```

Request and response bodies go to `DEBUG`:

```python
logging.getLogger("yookassax").setLevel(logging.DEBUG)
```

## What gets logged

| Level | Records |
|---|---|
| `INFO` | method, path, status code, duration, request identifier |
| `WARNING` | error responses, retries, connection failures |
| `DEBUG` | the same plus headers, request body and response body |

```
INFO  ЮKassa ответ: POST /payments -> 200 за 0.412 c, id: 3225ad37-000f-5001-8000-108ff2fd923d
WARN  ЮKassa ответ: GET /payments/p-1 -> 404 за 0.088 c, id: err-1
WARN  ЮKassa повтор: POST /payments, попытка 2 через 0.503 c, причина: ServerError
WARN  ЮKassa без ответа: POST /payments, попытка 1, причина: Connection reset
```

The messages are in Russian, like every runtime message in the library. The
request identifier is worth keeping: YooKassa support can look the request up by
it. The duration answers "why did the handler take a second", and the retry line
answers "why were there two calls".

## loguru

No separate support is needed: loguru intercepts standard `logging` with its own
handler, and the library's records join your own stream.

```python
import logging
import sys

from loguru import logger


class InterceptHandler(logging.Handler):
    def emit(self, record):
        logger.opt(depth=6, exception=record.exc_info).log(
            record.levelname, record.getMessage()
        )


logger.remove()
logger.add(sys.stdout)
logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)
```

After that the records look like this:

```
15:25:47 | INFO | ЮKassa ответ: POST /payments -> 200 за 0.412 c, id: p-1
```

## What never gets logged

**The `Authorization` header.** It carries the shop secret key or the OAuth
token, and a log lives longer and is read more widely than it seems while
debugging. The value is always replaced with `<скрыто>`, and a test keeps it
that way.

**Request and response bodies at `INFO`.** They contain the payer's personal
data: phone, email, receipt details. Turning `DEBUG` on in production should be
a deliberate and short-lived decision.

If your application already separates these modes with a flag of its own, tie
the logger level to it:

```python
level = logging.DEBUG if settings.LOG_PAYMENT_BODIES else logging.INFO
logging.getLogger("yookassax").setLevel(level)
```

## Structured logs

Records are formatted lazily through `logging` arguments, so a handler receives
both the template and the values:

```python
class JsonHandler(logging.Handler):
    def emit(self, record):
        print({"message": record.getMessage(), "logger": record.name})


handler = JsonHandler()
logging.getLogger("yookassax").addHandler(handler)
```

For metrics it is easier to catch the library's exceptions than to parse
strings: `RateLimited` for 429, `ServerError` for 500, `TransportError` for
dropped connections. Details in the [errors guide](14-errors.md).
