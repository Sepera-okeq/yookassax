"""Операции с настройками магазина и подписками: /me и /webhooks."""

from __future__ import annotations

from ..models import Me, Page, Webhook
from ..operation import Operation

__all__ = ["get_me", "webhook_add", "webhook_list", "webhook_remove"]


def get_me() -> Operation:
    """Запросить настройки магазина."""
    return Operation(method="GET", path="/me", parse=Me.from_api)


def webhook_list() -> Operation:
    """Список подписок на уведомления."""
    return Operation(
        method="GET",
        path="/webhooks",
        parse=lambda payload: Page.of(Webhook, payload),
    )


def webhook_add(
    event: str,
    url: str,
    *,
    idempotency_key: str | None = None,
) -> Operation:
    """Подписаться на событие, например payment.succeeded.

    Работает только с OAuth-токеном: секретный ключ магазина такие запросы
    не выполняет.
    """
    return Operation(
        method="POST",
        path="/webhooks",
        body={"event": event, "url": url},
        parse=Webhook.from_api,
        idempotent=True,
        idempotency_key=idempotency_key,
    )


def webhook_remove(
    webhook_id: str,
    *,
    idempotency_key: str | None = None,
) -> Operation:
    """Отписаться от события.

    API отвечает без тела, поэтому операция возвращает True.
    """
    return Operation(
        method="DELETE",
        path=f"/webhooks/{webhook_id}",
        parse=lambda payload: True,
        idempotent=True,
        idempotency_key=idempotency_key,
    )
