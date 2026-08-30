"""Операции с возвратами: /refunds."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from ..models import Page, Refund
from ..operation import Operation

__all__ = ["create", "get", "list_page"]

BASE_PATH = "/refunds"


def create(
    params: Mapping[str, Any],
    *,
    idempotency_key: str | None = None,
) -> Operation:
    """Создать возврат. В теле нужны payment_id и amount."""
    return Operation(
        method="POST",
        path=BASE_PATH,
        body=params,
        parse=Refund.from_api,
        idempotent=True,
        idempotency_key=idempotency_key,
    )


def get(refund_id: str) -> Operation:
    """Запросить состояние возврата."""
    return Operation(
        method="GET",
        path=f"{BASE_PATH}/{refund_id}",
        parse=Refund.from_api,
    )


def list_page(**filters: Any) -> Operation:
    """Запросить страницу списка возвратов."""
    return Operation(
        method="GET",
        path=BASE_PATH,
        params=filters,
        parse=lambda payload: Page.of(Refund, payload),
    )
