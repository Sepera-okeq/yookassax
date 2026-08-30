"""Входящие уведомления от ЮKassa.

Уведомление это POST от ЮKassa на ваш URL. Тело не подписано, поэтому порядок
работы такой:

1. проверить адрес отправителя через is_trusted_ip и отсечь подделку;
2. разобрать тело через parse и получить событие с объектом;
3. запросить объект через API и принимать решение по ответу API, а не по телу
   уведомления;
4. ответить 200 как можно быстрее, иначе ЮKassa будет повторять доставку и
   обработчик получит то же событие ещё раз.

Третий пункт не перестраховка. Сумма из тела напрямую управляет деньгами, а
подменить её проще, чем кажется: достаточно, чтобы запрос прошёл через ваш же
прокси или чтобы адрес отправителя оказался подделан.

Пример для FastAPI:

    from fastapi import Request
    from yookassax import webhooks

    @app.post("/webhook")
    async def handle(request: Request):
        ip = request.headers.get("X-Real-IP", "")
        if not webhooks.is_trusted_ip(ip):
            return Response(status_code=403)

        notification = webhooks.parse(await request.json())
        if notification.is_payment_succeeded:
            payment = await kassa.payments.get(notification.object.id)
            if payment.is_succeeded:
                ...
        return {"ok": True}
"""

from .notification import EVENTS, Notification, parse
from .sources import YOOKASSA_NETWORKS, is_trusted_ip

__all__ = [
    "EVENTS",
    "Notification",
    "YOOKASSA_NETWORKS",
    "is_trusted_ip",
    "parse",
]
