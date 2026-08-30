"""Операции с платежами: /payments."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from ..models import Page, Payment
from ..operation import Operation

__all__ = ["cancel", "capture", "create", "get", "list_page"]

BASE_PATH = "/payments"


def create(
    params: Mapping[str, Any],
    *,
    idempotency_key: str | None = None,
) -> Operation:
    """Создать платёж."""
    return Operation(
        method="POST",
        path=BASE_PATH,
        body=params,
        parse=Payment.from_api,
        idempotent=True,
        idempotency_key=idempotency_key,
    )


def get(payment_id: str) -> Operation:
    """Запросить текущее состояние платежа."""
    return Operation(
        method="GET",
        path=f"{BASE_PATH}/{payment_id}",
        parse=Payment.from_api,
    )


def capture(
    payment_id: str,
    params: Mapping[str, Any] | None = None,
    *,
    idempotency_key: str | None = None,
) -> Operation:
    """Подтвердить платёж в статусе waiting_for_capture."""
    return Operation(
        method="POST",
        path=f"{BASE_PATH}/{payment_id}/capture",
        body=params or {},
        parse=Payment.from_api,
        idempotent=True,
        idempotency_key=idempotency_key,
    )


def cancel(
    payment_id: str,
    *,
    idempotency_key: str | None = None,
) -> Operation:
    """Отменить платёж в статусе waiting_for_capture."""
    return Operation(
        method="POST",
        path=f"{BASE_PATH}/{payment_id}/cancel",
        body={},
        parse=Payment.from_api,
        idempotent=True,
        idempotency_key=idempotency_key,
    )


def list_page(**filters: Any) -> Operation:
    """Запросить страницу списка платежей."""
    return Operation(
        method="GET",
        path=BASE_PATH,
        params=filters,
        parse=lambda payload: Page.of(Payment, payload),
    )
