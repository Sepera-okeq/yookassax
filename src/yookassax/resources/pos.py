"""Ресурсы кассовых ссылок и справочника СБП."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from ..models import Page, PosLink
from ..operations import pos as ops
from .base import AsyncResource, Resource

__all__ = ["AsyncPosLinks", "AsyncSbpBanks", "PosLinks", "SbpBanks"]


class PosLinks(Resource):
    """Ссылки на оплату в кассе."""

    def create(
        self,
        params: Mapping[str, Any],
        *,
        idempotency_key: str | None = None,
    ) -> PosLink:
        """Создать ссылку."""
        return self._client.send(
            ops.pos_link_create(params, idempotency_key=idempotency_key)
        )

    def get(self, pos_link_id: str) -> PosLink:
        """Запросить ссылку."""
        return self._client.send(ops.pos_link_get(pos_link_id))

    def activate(
        self,
        pos_link_id: str,
        *,
        idempotency_key: str | None = None,
    ) -> PosLink:
        """Активировать ссылку."""
        return self._client.send(
            ops.pos_link_activate(pos_link_id, idempotency_key=idempotency_key)
        )

    def deactivate(
        self,
        pos_link_id: str,
        *,
        idempotency_key: str | None = None,
    ) -> PosLink:
        """Деактивировать ссылку."""
        return self._client.send(
            ops.pos_link_deactivate(pos_link_id, idempotency_key=idempotency_key)
        )

    def change_recipient(
        self,
        pos_link_id: str,
        params: Mapping[str, Any],
        *,
        idempotency_key: str | None = None,
    ) -> PosLink:
        """Сменить получателя по ссылке."""
        return self._client.send(
            ops.pos_link_change_recipient(
                pos_link_id, params, idempotency_key=idempotency_key
            )
        )


class AsyncPosLinks(AsyncResource):
    """Кассовые ссылки в асинхронном режиме."""

    async def create(
        self,
        params: Mapping[str, Any],
        *,
        idempotency_key: str | None = None,
    ) -> PosLink:
        """Создать ссылку."""
        return await self._client.send(
            ops.pos_link_create(params, idempotency_key=idempotency_key)
        )

    async def get(self, pos_link_id: str) -> PosLink:
        """Запросить ссылку."""
        return await self._client.send(ops.pos_link_get(pos_link_id))

    async def activate(
        self,
        pos_link_id: str,
        *,
        idempotency_key: str | None = None,
    ) -> PosLink:
        """Активировать ссылку."""
        return await self._client.send(
            ops.pos_link_activate(pos_link_id, idempotency_key=idempotency_key)
        )

    async def deactivate(
        self,
        pos_link_id: str,
        *,
        idempotency_key: str | None = None,
    ) -> PosLink:
        """Деактивировать ссылку."""
        return await self._client.send(
            ops.pos_link_deactivate(pos_link_id, idempotency_key=idempotency_key)
        )

    async def change_recipient(
        self,
        pos_link_id: str,
        params: Mapping[str, Any],
        *,
        idempotency_key: str | None = None,
    ) -> PosLink:
        """Сменить получателя по ссылке."""
        return await self._client.send(
            ops.pos_link_change_recipient(
                pos_link_id, params, idempotency_key=idempotency_key
            )
        )


class SbpBanks(Resource):
    """Справочник банков СБП."""

    def list(self) -> Page:
        """Список банков, доступных для оплаты через СБП."""
        return self._client.send(ops.sbp_bank_list())


class AsyncSbpBanks(AsyncResource):
    """Справочник банков СБП в асинхронном режиме."""

    async def list(self) -> Page:
        """Список банков, доступных для оплаты через СБП."""
        return await self._client.send(ops.sbp_bank_list())
