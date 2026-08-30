"""Операции с чеками: /receipts."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from ..models import Page, Receipt
from ..operation import Operation

__all__ = ["create", "get", "list_page"]

BASE_PATH = "/receipts"


def create(
    params: Mapping[str, Any],
    *,
    idempotency_key: str | None = None,
) -> Operation:
    """Пробить чек."""
    return Operation(
        method="POST",
        path=BASE_PATH,
        body=params,
        parse=Receipt.from_api,
        idempotent=True,
        idempotency_key=idempotency_key,
    )


def get(receipt_id: str) -> Operation:
    """Запросить чек."""
    return Operation(
        method="GET",
        path=f"{BASE_PATH}/{receipt_id}",
        parse=Receipt.from_api,
    )


def list_page(**filters: Any) -> Operation:
    """Запросить страницу списка чеков."""
    return Operation(
        method="GET",
        path=BASE_PATH,
        params=filters,
        parse=lambda payload: Page.of(Receipt, payload),
    )
