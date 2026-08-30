# yookassax

Русский | [English](https://github.com/Sepera-okeq/yookassax/blob/main/README.en.md)

> **Неофициальная библиотека.** Проект не связан с ЮKassa и ЮMoney, ими не
> поддерживается и их продуктом не является. Официальный SDK лежит
> [здесь](https://git.yoomoney.ru/projects/SDK/repos/yookassa-sdk-python).
> ЮKassa и ЮMoney — товарные знаки своих владельцев.

Неофициальный клиент [ЮKassa](https://yookassa.ru/developers/api) для Python
в двух режимах: синхронном и асинхронном. Типизированные модели, разбор
уведомлений, идемпотентность и повторы из коробки.

```bash
pip install yookassax
```

Требуется Python 3.10 или новее. Единственная зависимость: `httpx`.

## Быстрый старт

Синхронно:

```python
from yookassax import YooKassa

with YooKassa(shop_id="123456", secret_key="live_...") as kassa:
    payment = kassa.payments.create({
        "amount": {"value": "100.00", "currency": "RUB"},
        "confirmation": {"type": "redirect", "return_url": "https://example.com/done"},
        "capture": True,
        "description": "Заказ 42",
    })
    print(payment.confirmation_url)
```

Асинхронно, то же самое:

```python
from yookassax import AsyncYooKassa

async with AsyncYooKassa(shop_id="123456", secret_key="live_...") as kassa:
    payment = await kassa.payments.create({
        "amount": {"value": "100.00", "currency": "RUB"},
        "confirmation": {"type": "redirect", "return_url": "https://example.com/done"},
        "capture": True,
    })
```

Наборы методов у режимов одинаковые, это проверяется тестом. Переход с одного
на другой сводится к добавлению `await`.

## Примеры

Все сценарии из официальной документации, оба режима, два языка:
[русский](https://github.com/Sepera-okeq/yookassax/blob/main/docs/examples/ru/README.md),
[English](https://github.com/Sepera-okeq/yookassax/blob/main/docs/examples/en/README.md).

| | |
|---|---|
| [Настройка клиента](https://github.com/Sepera-okeq/yookassax/blob/main/docs/examples/ru/01-configuration.md) | аутентификация, магазин, подписки |
| [Платежи](https://github.com/Sepera-okeq/yookassax/blob/main/docs/examples/ru/02-payments.md) | создание, подтверждение, отмена, списки |
| [Возвраты](https://github.com/Sepera-okeq/yookassax/blob/main/docs/examples/ru/03-refunds.md) | полные и частичные |
| [Чеки](https://github.com/Sepera-okeq/yookassax/blob/main/docs/examples/ru/04-receipts.md) | 54-ФЗ, маркированные товары |
| [Сделки](https://github.com/Sepera-okeq/yookassax/blob/main/docs/examples/ru/05-deals.md) | безопасная сделка целиком |
| [Выплаты](https://github.com/Sepera-okeq/yookassax/blob/main/docs/examples/ru/06-payouts.md) | карта, СБП, кошелёк, самозанятые |
| [Самозанятые](https://github.com/Sepera-okeq/yookassax/blob/main/docs/examples/ru/07-self-employed.md) | регистрация и подтверждение |
| [Персональные данные](https://github.com/Sepera-okeq/yookassax/blob/main/docs/examples/ru/08-personal-data.md) | получатели выплат |
| [Банки СБП](https://github.com/Sepera-okeq/yookassax/blob/main/docs/examples/ru/09-sbp-banks.md) | справочник |
| [Счета](https://github.com/Sepera-okeq/yookassax/blob/main/docs/examples/ru/10-invoices.md) | ссылка на оплату |
| [Способы оплаты](https://github.com/Sepera-okeq/yookassax/blob/main/docs/examples/ru/11-payment-methods.md) | подписки и автоплатежи |
| [Кассовые ссылки](https://github.com/Sepera-okeq/yookassax/blob/main/docs/examples/ru/12-pos-links.md) | статические QR-коды |
| [Уведомления](https://github.com/Sepera-okeq/yookassax/blob/main/docs/examples/ru/13-webhooks.md) | FastAPI, Django, Flask |
| [Ошибки и повторы](https://github.com/Sepera-okeq/yookassax/blob/main/docs/examples/ru/14-errors.md) | идемпотентность, обрывы связи |
| [Модели ответов](https://github.com/Sepera-okeq/yookassax/blob/main/docs/examples/ru/15-models.md) | все 73 модели и сверка со спецификацией |

## Чем отличается от официального SDK

**Ключи хранятся в экземпляре клиента.** Официальный SDK держит их в
`Configuration` на уровне класса. Если приложение работает с несколькими
магазинами из одного процесса, два платежа могут переписать токен друг другу
между настройкой и вызовом, и платёж уйдёт через чужой магазин. Здесь каждый
клиент носит свои ключи, и такой гонки не существует.

**Асинхронный режим настоящий.** Официальный SDK синхронный, внутри `requests`.
Вызов из асинхронного обработчика останавливает весь воркер: пока идёт
обращение к API, процесс не обслуживает никого.

**Ключ идемпотентности проставляется сам** на всех изменяющих запросах. Повтор
после обрыва связи идёт с тем же ключом, поэтому второго платежа не возникает.

**Повторы** на кодах 202, 429 и 500 с экспоненциальной паузой и дрожанием.
Ошибки данных (400, 404) не повторяются: второй такой же запрос даст тот же
ответ.

**Способ оплаты разбирается в модель своего типа.** Все 19 из спецификации:
`PaymentMethodBankCard`, `PaymentMethodSberLoan`,
`PaymentMethodElectronicCertificate` и так далее. Различать через `isinstance`,
[подробности](https://github.com/Sepera-okeq/yookassax/blob/main/docs/examples/ru/11-payment-methods.md#типы-способов-оплаты).

**Модели типизированы и терпимы к новым полям.** ЮKassa добавляет поля в
ответы; строгая модель превратила бы это в отказ обслуживать платежи. Всё
неизвестное складывается в `raw` и доступно через `extra`. Но не молча: на
каждое такое поле один раз выдаётся `UnknownFieldWarning`, иначе о новом поле
никто и не узнает.

**Билдеров нет.** Тело запроса это обычный словарь: он принимает новые поля
API сразу, а не после обновления библиотеки.

## Работа с платежами

```python
payment = kassa.payments.create({...})

payment.is_pending             # ждём оплату
payment.is_waiting_for_capture # деньги захолдированы, нужен capture или cancel
payment.is_succeeded           # деньги у магазина
payment.is_canceled            # деньги у плательщика

payment.amount.value           # Decimal("100.00"), не float
payment.created_at             # datetime с часовым поясом
payment.confirmation_url       # куда вести плательщика, либо None

kassa.payments.capture(payment.id)
kassa.payments.cancel(payment.id)
```

## Списки

```python
page = kassa.payments.list(status="succeeded", limit=50)
for payment in page:
    print(payment.id)

if page.has_more:
    next_page = kassa.payments.list(status="succeeded", cursor=page.next_cursor)
```

Или без ручного перелистывания:

```python
for payment in kassa.payments.iterate(status="succeeded"):
    print(payment.id)
```

В асинхронном режиме то же самое через `async for`.

## Уведомления

Тело уведомления ЮKassa не подписывает, поэтому единственная встроенная
проверка это адрес отправителя. Её недостаточно: решение о деньгах принимайте
по ответу API, а не по телу уведомления.

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

Берите достоверный адрес отправителя. За обратным прокси это тот, который
прокси проставляет сам, обычно `X-Real-IP` из nginx. Левый элемент
`X-Forwarded-For` подставляет клиент, и проверка теряет смысл.

Отвечайте 200 быстро: иначе ЮKassa повторит доставку, и обработчик получит то
же событие ещё раз.

## Ошибки

```python
from yookassax import BadRequest, Forbidden, TransportError, YooKassaError

try:
    payment = kassa.payments.create({...})
except Forbidden:
    # магазину не разрешена операция, частый случай: не подключён рекуррент
    ...
except BadRequest as error:
    print(error.code, error.description, error.parameter)
except TransportError:
    # ответа не было вообще, состояние платежа неизвестно
    ...
except YooKassaError:
    ...
```

`TransportError` стоит отдельно от остальных намеренно: если создание платежа
упало с ним, неизвестно, создан платёж или нет.

## Новые поля в ответах

Поле, которого нет в модели, разбор не роняет, но и не скрывает:

```python
payment = kassa.payments.get(payment_id)
# UnknownFieldWarning: Payment: в ответе API есть поля, которых нет в модели:
# loyalty_bonus. Значения доступны через extra(), но, возможно, стоит обновить
# yookassax.

payment.extra("loyalty_bonus")
```

Предупреждение указывает на строку вашего кода и выдаётся один раз на пару
"модель плюс поле" за жизнь процесса: страница из ста платежей даст одну
строку, а не сто. Отключается штатным фильтром:

```python
import warnings
from yookassax import UnknownFieldWarning

warnings.filterwarnings("ignore", category=UnknownFieldWarning)
```

## Доступные ресурсы

`payments`, `refunds`, `receipts`, `payouts`, `webhooks`, `settings`,
`payment_methods`, `deals`, `invoices`, `personal_data`, `self_employed`,
`pos_links`, `sbp_banks`.

Покрыты все маршруты официальной спецификации OpenAPI. Полнота проверяется
тестом.

## OAuth

Для работы с чужими магазинами:

```python
kassa = YooKassa(oauth_token="токен, выданный магазином")
```

Одновременно с `shop_id` и `secret_key` не задаётся: клиент откажется
собираться, чтобы не выбирать за вас.

## Эндпоинт, которого ещё нет в библиотеке

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

## Для ИИ-ассистентов

В каталоге `docs` лежит [`llms.txt`](https://github.com/Sepera-okeq/yookassax/blob/main/docs/llms.txt): полный справочник по
библиотеке одним файлом, чтобы вставить в контекст модели. Английская
версия: [`llms.en.txt`](https://github.com/Sepera-okeq/yookassax/blob/main/docs/llms.en.txt).

## Разработка

```bash
pip install -e ".[dev]"
pytest
ruff check .
mypy src
```

Тесты не ходят в сеть. Отдельно есть прогон по живому API, он требует ключи
тестового магазина и без них пропускается:

```bash
export YOOKASSA_SHOP_ID=... YOOKASSA_SECRET_KEY=test_...
pytest tests/integration
```

## Лицензия

MIT.
