"""Ресурс сохранённых способов оплаты."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from ..models import PaymentMethod
from ..operations import payment_methods as ops
from .base import AsyncResource, Resource

__all__ = ["AsyncPaymentMethods", "PaymentMethods"]


class PaymentMethods(Resource):
    """Сохранённые способы оплаты для повторных списаний."""

    def create(
        self,
        params: Mapping[str, Any],
        *,
        idempotency_key: str | None = None,
    ) -> PaymentMethod:
        """Сохранить способ оплаты.

        Магазину должны быть разрешены рекуррентные платежи, иначе ЮKassa
        ответит 403.
        """
        return self._client.send(ops.create(params, idempotency_key=idempotency_key))

    def get(self, payment_method_id: str) -> PaymentMethod:
        """Запросить сохранённый способ оплаты."""
        return self._client.send(ops.get(payment_method_id))


class AsyncPaymentMethods(AsyncResource):
    """Сохранённые способы оплаты в асинхронном режиме."""

    async def create(
        self,
        params: Mapping[str, Any],
        *,
        idempotency_key: str | None = None,
    ) -> PaymentMethod:
        """Сохранить способ оплаты."""
        return await self._client.send(
            ops.create(params, idempotency_key=idempotency_key)
        )

    async def get(self, payment_method_id: str) -> PaymentMethod:
        """Запросить сохранённый способ оплаты."""
        return await self._client.send(ops.get(payment_method_id))
