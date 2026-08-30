"""Ресурс возвратов."""

from __future__ import annotations

from collections.abc import AsyncIterator, Iterator, Mapping
from typing import Any

from ..models import Page, Refund
from ..operations import refunds as ops
from .base import AsyncResource, Resource, iterate_pages, iterate_pages_async

__all__ = ["AsyncRefunds", "Refunds"]


class Refunds(Resource):
    """Возвраты по платежам."""

    def create(
        self,
        params: Mapping[str, Any],
        *,
        idempotency_key: str | None = None,
    ) -> Refund:
        """Вернуть деньги плательщику.

        В теле обязательны payment_id и amount. Сумма возврата не может
        превышать неотозванный остаток платежа.
        """
        return self._client.send(ops.create(params, idempotency_key=idempotency_key))

    def get(self, refund_id: str) -> Refund:
        """Запросить состояние возврата."""
        return self._client.send(ops.get(refund_id))

    def list(self, **filters: Any) -> Page:
        """Страница возвратов."""
        return self._client.send(ops.list_page(**filters))

    def iterate(self, **filters: Any) -> Iterator[Refund]:
        """Все возвраты по фильтру."""
        return iterate_pages(self._client, ops.list_page, filters)


class AsyncRefunds(AsyncResource):
    """Возвраты в асинхронном режиме."""

    async def create(
        self,
        params: Mapping[str, Any],
        *,
        idempotency_key: str | None = None,
    ) -> Refund:
        """Вернуть деньги плательщику."""
        return await self._client.send(
            ops.create(params, idempotency_key=idempotency_key)
        )

    async def get(self, refund_id: str) -> Refund:
        """Запросить состояние возврата."""
        return await self._client.send(ops.get(refund_id))

    async def list(self, **filters: Any) -> Page:
        """Страница возвратов."""
        return await self._client.send(ops.list_page(**filters))

    def iterate(self, **filters: Any) -> AsyncIterator[Refund]:
        """Все возвраты по фильтру."""
        return iterate_pages_async(self._client, ops.list_page, filters)
