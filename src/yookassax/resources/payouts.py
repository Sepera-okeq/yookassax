"""Ресурс выплат."""

from __future__ import annotations

from collections.abc import AsyncIterator, Iterator, Mapping
from typing import Any

from ..models import Page, Payout
from ..operations import payouts as ops
from .base import AsyncResource, Resource, iterate_pages, iterate_pages_async

__all__ = ["AsyncPayouts", "Payouts"]


class Payouts(Resource):
    """Выплаты продавцам и самозанятым."""

    def create(
        self,
        params: Mapping[str, Any],
        *,
        idempotency_key: str | None = None,
    ) -> Payout:
        """Создать выплату."""
        return self._client.send(ops.create(params, idempotency_key=idempotency_key))

    def get(self, payout_id: str) -> Payout:
        """Запросить состояние выплаты."""
        return self._client.send(ops.get(payout_id))

    def list(self, **filters: Any) -> Page:
        """Страница выплат."""
        return self._client.send(ops.list_page(**filters))

    def iterate(self, **filters: Any) -> Iterator[Payout]:
        """Все выплаты по фильтру."""
        return iterate_pages(self._client, ops.list_page, filters)

    def search(self, **filters: Any) -> Page:
        """Найти выплаты, в том числе по метаданным.

        В отличие от list доступен фильтр metadata.
        """
        return self._client.send(ops.search(**filters))


class AsyncPayouts(AsyncResource):
    """Выплаты в асинхронном режиме."""

    async def create(
        self,
        params: Mapping[str, Any],
        *,
        idempotency_key: str | None = None,
    ) -> Payout:
        """Создать выплату."""
        return await self._client.send(
            ops.create(params, idempotency_key=idempotency_key)
        )

    async def get(self, payout_id: str) -> Payout:
        """Запросить состояние выплаты."""
        return await self._client.send(ops.get(payout_id))

    async def list(self, **filters: Any) -> Page:
        """Страница выплат."""
        return await self._client.send(ops.list_page(**filters))

    def iterate(self, **filters: Any) -> AsyncIterator[Payout]:
        """Все выплаты по фильтру."""
        return iterate_pages_async(self._client, ops.list_page, filters)

    async def search(self, **filters: Any) -> Page:
        """Найти выплаты, в том числе по метаданным."""
        return await self._client.send(ops.search(**filters))
