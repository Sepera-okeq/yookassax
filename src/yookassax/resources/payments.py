"""Ресурс платежей.

Методы описаны явно, а не собраны через __getattr__, хотя динамика вышла бы
короче. Явные методы дают автодополнение, проверку типов и читаемость. Тело
каждого метода состоит из одной строки: вся логика живёт в каталоге операций,
поэтому синхронная и асинхронная версии не расходятся.
"""

from __future__ import annotations

from collections.abc import AsyncIterator, Iterator, Mapping
from typing import Any

from ..models import Page, Payment
from ..operations import payments as ops
from .base import AsyncResource, Resource, iterate_pages, iterate_pages_async

__all__ = ["AsyncPayments", "Payments"]


class Payments(Resource):
    """Платежи: создание, статус, подтверждение, отмена, списки."""

    def create(
        self,
        params: Mapping[str, Any],
        *,
        idempotency_key: str | None = None,
    ) -> Payment:
        """Создать платёж.

        Ключ идемпотентности проставляется автоматически. Свой стоит задавать,
        когда повтор возможен со стороны вашего кода: второй вызов с тем же
        ключом вернёт уже созданный платёж, а не создаст новый.
        """
        return self._client.send(ops.create(params, idempotency_key=idempotency_key))

    def get(self, payment_id: str) -> Payment:
        """Запросить текущее состояние платежа.

        Это единственный надёжный источник истины о платеже. Телу уведомления
        доверять нельзя: оно не подписано.
        """
        return self._client.send(ops.get(payment_id))

    def capture(
        self,
        payment_id: str,
        params: Mapping[str, Any] | None = None,
        *,
        idempotency_key: str | None = None,
    ) -> Payment:
        """Подтвердить платёж в статусе waiting_for_capture.

        Без подтверждения захолдированные деньги вернутся плательщику.
        """
        return self._client.send(
            ops.capture(payment_id, params, idempotency_key=idempotency_key)
        )

    def cancel(
        self,
        payment_id: str,
        *,
        idempotency_key: str | None = None,
    ) -> Payment:
        """Отменить платёж в статусе waiting_for_capture."""
        return self._client.send(
            ops.cancel(payment_id, idempotency_key=idempotency_key)
        )

    def list(self, **filters: Any) -> Page:
        """Страница платежей.

        Фильтры совпадают с документацией API: status, created_at.gte, limit
        и другие.
        """
        return self._client.send(ops.list_page(**filters))

    def iterate(self, **filters: Any) -> Iterator[Payment]:
        """Все платежи по фильтру, курсоры перелистываются автоматически."""
        return iterate_pages(self._client, ops.list_page, filters)


class AsyncPayments(AsyncResource):
    """Платежи в асинхронном режиме. Набор методов тот же, что у Payments."""

    async def create(
        self,
        params: Mapping[str, Any],
        *,
        idempotency_key: str | None = None,
    ) -> Payment:
        """Создать платёж."""
        return await self._client.send(
            ops.create(params, idempotency_key=idempotency_key)
        )

    async def get(self, payment_id: str) -> Payment:
        """Запросить текущее состояние платежа."""
        return await self._client.send(ops.get(payment_id))

    async def capture(
        self,
        payment_id: str,
        params: Mapping[str, Any] | None = None,
        *,
        idempotency_key: str | None = None,
    ) -> Payment:
        """Подтвердить платёж в статусе waiting_for_capture."""
        return await self._client.send(
            ops.capture(payment_id, params, idempotency_key=idempotency_key)
        )

    async def cancel(
        self,
        payment_id: str,
        *,
        idempotency_key: str | None = None,
    ) -> Payment:
        """Отменить платёж в статусе waiting_for_capture."""
        return await self._client.send(
            ops.cancel(payment_id, idempotency_key=idempotency_key)
        )

    async def list(self, **filters: Any) -> Page:
        """Страница платежей."""
        return await self._client.send(ops.list_page(**filters))

    def iterate(self, **filters: Any) -> AsyncIterator[Payment]:
        """Все платежи по фильтру, курсоры перелистываются автоматически."""
        return iterate_pages_async(self._client, ops.list_page, filters)
