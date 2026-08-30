# Логи

Библиотека пишет каждое обращение к API стандартным `logging` в логгер
`yookassax`. Своего логгера она не навязывает: приложения на loguru
подхватывают эти записи перехватчиком, приложения на `logging` — как обычно.

* [Включить](#включить)
* [Что попадает в лог](#что-попадает-в-лог)
* [loguru](#loguru)
* [Чего в логе нет](#чего-в-логе-нет)
* [Структурные логи](#структурные-логи)

## Включить

По умолчанию у логгера нет обработчика, поэтому пишет он только там, где
логирование настроено:

```python
import logging

logging.basicConfig(level=logging.INFO)
logging.getLogger("yookassax").setLevel(logging.INFO)
```

Тела запросов и ответов идут на `DEBUG`:

```python
logging.getLogger("yookassax").setLevel(logging.DEBUG)
```

## Что попадает в лог

| Уровень | Записи |
|---|---|
| `INFO` | метод, путь, код ответа, длительность, идентификатор запроса |
| `WARNING` | ответы с ошибкой, повторы, обрывы связи |
| `DEBUG` | то же плюс заголовки, тело запроса и тело ответа |

```
INFO  ЮKassa ответ: POST /payments -> 200 за 0.412 c, id: 3225ad37-000f-5001-8000-108ff2fd923d
WARN  ЮKassa ответ: GET /payments/p-1 -> 404 за 0.088 c, id: err-1
WARN  ЮKassa повтор: POST /payments, попытка 2 через 0.503 c, причина: ServerError
WARN  ЮKassa без ответа: POST /payments, попытка 1, причина: Connection reset
```

Идентификатор запроса стоит хранить: по нему поддержка ЮKassa находит запрос
у себя. Длительность отвечает на вопрос «почему обработчик отвечал секунду», а
строка про повтор — «почему их было две».

## loguru

Отдельной поддержки не нужно: loguru перехватывает стандартный `logging` своим
обработчиком, и записи библиотеки идут в общий поток вместе с вашими.

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

После этого записи выглядят так:

```
15:25:47 | INFO | ЮKassa ответ: POST /payments -> 200 за 0.412 c, id: p-1
```

## Чего в логе нет

**Заголовка `Authorization`.** В нём секретный ключ магазина или OAuth-токен, а
лог живёт дольше и читается шире, чем кажется в момент отладки. На месте ключа
всегда `<скрыто>`, это проверяется тестом.

**Тел запроса и ответа на уровне `INFO`.** Там персональные данные плательщика:
телефон, почта, реквизиты чека. Включать `DEBUG` в проде стоит осознанно и
ненадолго.

Если приложение уже разделяет эти режимы своим тумблером, привяжите к нему
уровень логгера:

```python
level = logging.DEBUG if settings.LOG_PAYMENT_BODIES else logging.INFO
logging.getLogger("yookassax").setLevel(level)
```

## Структурные логи

Записи форматируются лениво, через аргументы `logging`, поэтому обработчик
получает и шаблон, и значения:

```python
class JsonHandler(logging.Handler):
    def emit(self, record):
        print({"message": record.getMessage(), "logger": record.name})


handler = JsonHandler()
logging.getLogger("yookassax").addHandler(handler)
```

Для сбора метрик удобнее не парсить строки, а ловить исключения библиотеки:
`RateLimited` для 429, `ServerError` для 500, `TransportError` для обрывов.
Подробности в [примерах по ошибкам](14-errors.md).
