"""Ресурсы настроек магазина и подписок на уведомления."""

from __future__ import annotations

from ..models import Me, Page, Webhook
from ..operations import shop as ops
from .base import AsyncResource, Resource

__all__ = ["AsyncSettings", "AsyncWebhooks", "Settings", "Webhooks"]


class Settings(Resource):
    """Настройки магазина."""

    def get(self) -> Me:
        """Кто мы для ЮKassa.

        Стоит вызывать на старте приложения: так тестовые ключи в боевом
        окружении обнаруживаются сразу, а не на первом платеже.
        """
        return self._client.send(ops.get_me())


class AsyncSettings(AsyncResource):
    """Настройки магазина в асинхронном режиме."""

    async def get(self) -> Me:
        """Кто мы для ЮKassa."""
        return await self._client.send(ops.get_me())


class Webhooks(Resource):
    """Подписки на уведомления.

    Не путайте с разбором самих уведомлений: он в пакете yookassax.webhooks.
    Управление подписками работает только с OAuth-токеном.
    """

    def list(self) -> Page:
        """Действующие подписки."""
        return self._client.send(ops.webhook_list())

    def add(
        self,
        event: str,
        url: str,
        *,
        idempotency_key: str | None = None,
    ) -> Webhook:
        """Подписаться на событие, например payment.succeeded."""
        return self._client.send(
            ops.webhook_add(event, url, idempotency_key=idempotency_key)
        )

    def remove(
        self,
        webhook_id: str,
        *,
        idempotency_key: str | None = None,
    ) -> bool:
        """Отписаться от события."""
        return self._client.send(
            ops.webhook_remove(webhook_id, idempotency_key=idempotency_key)
        )


class AsyncWebhooks(AsyncResource):
    """Подписки на уведомления в асинхронном режиме."""

    async def list(self) -> Page:
        """Действующие подписки."""
        return await self._client.send(ops.webhook_list())

    async def add(
        self,
        event: str,
        url: str,
        *,
        idempotency_key: str | None = None,
    ) -> Webhook:
        """Подписаться на событие."""
        return await self._client.send(
            ops.webhook_add(event, url, idempotency_key=idempotency_key)
        )

    async def remove(
        self,
        webhook_id: str,
        *,
        idempotency_key: str | None = None,
    ) -> bool:
        """Отписаться от события."""
        return await self._client.send(
            ops.webhook_remove(webhook_id, idempotency_key=idempotency_key)
        )
