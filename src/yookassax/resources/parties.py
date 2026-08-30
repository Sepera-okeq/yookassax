"""Ресурсы контрагентов: счета, персональные данные, самозанятые.

Имена ресурсов совпадают с именами моделей, поэтому модели импортируются под
псевдонимами с суффиксом Model. Так в аннотациях видно, что возвращается
именно модель, а не ресурс.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from ..models import Invoice as InvoiceModel
from ..models import PersonalData as PersonalDataModel
from ..models import SelfEmployed as SelfEmployedModel
from ..operations import parties as ops
from .base import AsyncResource, Resource

__all__ = [
    "AsyncInvoices",
    "AsyncPersonalData",
    "AsyncSelfEmployed",
    "Invoices",
    "PersonalData",
    "SelfEmployed",
]


class Invoices(Resource):
    """Счета на оплату."""

    def create(
        self,
        params: Mapping[str, Any],
        *,
        idempotency_key: str | None = None,
    ) -> InvoiceModel:
        """Выставить счёт."""
        return self._client.send(
            ops.invoice_create(params, idempotency_key=idempotency_key)
        )

    def get(self, invoice_id: str) -> InvoiceModel:
        """Запросить счёт."""
        return self._client.send(ops.invoice_get(invoice_id))


class AsyncInvoices(AsyncResource):
    """Счета в асинхронном режиме."""

    async def create(
        self,
        params: Mapping[str, Any],
        *,
        idempotency_key: str | None = None,
    ) -> InvoiceModel:
        """Выставить счёт."""
        return await self._client.send(
            ops.invoice_create(params, idempotency_key=idempotency_key)
        )

    async def get(self, invoice_id: str) -> InvoiceModel:
        """Запросить счёт."""
        return await self._client.send(ops.invoice_get(invoice_id))


class PersonalData(Resource):
    """Персональные данные получателей выплат.

    Данные хранятся на стороне ЮKassa ограниченное время, срок в поле
    expires_at модели.
    """

    def create(
        self,
        params: Mapping[str, Any],
        *,
        idempotency_key: str | None = None,
    ) -> PersonalDataModel:
        """Передать персональные данные в ЮKassa."""
        return self._client.send(
            ops.personal_data_create(params, idempotency_key=idempotency_key)
        )

    def get(self, personal_data_id: str) -> PersonalDataModel:
        """Запросить состояние переданных данных."""
        return self._client.send(ops.personal_data_get(personal_data_id))


class AsyncPersonalData(AsyncResource):
    """Персональные данные в асинхронном режиме."""

    async def create(
        self,
        params: Mapping[str, Any],
        *,
        idempotency_key: str | None = None,
    ) -> PersonalDataModel:
        """Передать персональные данные в ЮKassa."""
        return await self._client.send(
            ops.personal_data_create(params, idempotency_key=idempotency_key)
        )

    async def get(self, personal_data_id: str) -> PersonalDataModel:
        """Запросить состояние переданных данных."""
        return await self._client.send(ops.personal_data_get(personal_data_id))


class SelfEmployed(Resource):
    """Самозанятые получатели выплат."""

    def create(
        self,
        params: Mapping[str, Any],
        *,
        idempotency_key: str | None = None,
    ) -> SelfEmployedModel:
        """Зарегистрировать самозанятого."""
        return self._client.send(
            ops.self_employed_create(params, idempotency_key=idempotency_key)
        )

    def get(self, self_employed_id: str) -> SelfEmployedModel:
        """Запросить состояние регистрации."""
        return self._client.send(ops.self_employed_get(self_employed_id))


class AsyncSelfEmployed(AsyncResource):
    """Самозанятые в асинхронном режиме."""

    async def create(
        self,
        params: Mapping[str, Any],
        *,
        idempotency_key: str | None = None,
    ) -> SelfEmployedModel:
        """Зарегистрировать самозанятого."""
        return await self._client.send(
            ops.self_employed_create(params, idempotency_key=idempotency_key)
        )

    async def get(self, self_employed_id: str) -> SelfEmployedModel:
        """Запросить состояние регистрации."""
        return await self._client.send(ops.self_employed_get(self_employed_id))
