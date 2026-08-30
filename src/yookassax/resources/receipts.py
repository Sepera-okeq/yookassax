"""Ресурс чеков."""

from __future__ import annotations

from collections.abc import AsyncIterator, Iterator, Mapping
from typing import Any

from ..models import Page, Receipt
from ..operations import receipts as ops
from .base import AsyncResource, Resource, iterate_pages, iterate_pages_async

__all__ = ["AsyncReceipts", "Receipts"]


class Receipts(Resource):
    """Чеки по 54-ФЗ."""

    def create(
        self,
        params: Mapping[str, Any],
        *,
        idempotency_key: str | None = None,
    ) -> Receipt:
        """Пробить чек."""
        return self._client.send(ops.create(params, idempotency_key=idempotency_key))

    def get(self, receipt_id: str) -> Receipt:
        """Запросить чек."""
        return self._client.send(ops.get(receipt_id))

    def list(self, **filters: Any) -> Page:
        """Страница чеков."""
        return self._client.send(ops.list_page(**filters))

    def iterate(self, **filters: Any) -> Iterator[Receipt]:
        """Все чеки по фильтру."""
        return iterate_pages(self._client, ops.list_page, filters)


class AsyncReceipts(AsyncResource):
    """Чеки в асинхронном режиме."""

    async def create(
        self,
        params: Mapping[str, Any],
        *,
        idempotency_key: str | None = None,
    ) -> Receipt:
        """Пробить чек."""
        return await self._client.send(
            ops.create(params, idempotency_key=idempotency_key)
        )

    async def get(self, receipt_id: str) -> Receipt:
        """Запросить чек."""
        return await self._client.send(ops.get(receipt_id))

    async def list(self, **filters: Any) -> Page:
        """Страница чеков."""
        return await self._client.send(ops.list_page(**filters))

    def iterate(self, **filters: Any) -> AsyncIterator[Receipt]:
        """Все чеки по фильтру."""
        return iterate_pages_async(self._client, ops.list_page, filters)
