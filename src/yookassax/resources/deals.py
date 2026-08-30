"""Ресурс сделок безопасной сделки."""

from __future__ import annotations

from collections.abc import AsyncIterator, Iterator, Mapping
from typing import Any

from ..models import Deal, Page
from ..operations import deals as ops
from .base import AsyncResource, Resource, iterate_pages, iterate_pages_async

__all__ = ["AsyncDeals", "Deals"]


class Deals(Resource):
    """Сделки: деньги держатся до выполнения обязательств продавцом."""

    def create(
        self,
        params: Mapping[str, Any],
        *,
        idempotency_key: str | None = None,
    ) -> Deal:
        """Создать сделку."""
        return self._client.send(ops.create(params, idempotency_key=idempotency_key))

    def get(self, deal_id: str) -> Deal:
        """Запросить сделку."""
        return self._client.send(ops.get(deal_id))

    def list(self, **filters: Any) -> Page:
        """Страница сделок."""
        return self._client.send(ops.list_page(**filters))

    def iterate(self, **filters: Any) -> Iterator[Deal]:
        """Все сделки по фильтру."""
        return iterate_pages(self._client, ops.list_page, filters)


class AsyncDeals(AsyncResource):
    """Сделки в асинхронном режиме."""

    async def create(
        self,
        params: Mapping[str, Any],
        *,
        idempotency_key: str | None = None,
    ) -> Deal:
        """Создать сделку."""
        return await self._client.send(
            ops.create(params, idempotency_key=idempotency_key)
        )

    async def get(self, deal_id: str) -> Deal:
        """Запросить сделку."""
        return await self._client.send(ops.get(deal_id))

    async def list(self, **filters: Any) -> Page:
        """Страница сделок."""
        return await self._client.send(ops.list_page(**filters))

    def iterate(self, **filters: Any) -> AsyncIterator[Deal]:
        """Все сделки по фильтру."""
        return iterate_pages_async(self._client, ops.list_page, filters)
