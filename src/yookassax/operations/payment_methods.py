"""Операции с сохранёнными способами оплаты: /payment_methods."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from ..models import PaymentMethod
from ..operation import Operation

__all__ = ["create", "get"]

BASE_PATH = "/payment_methods"


def create(
    params: Mapping[str, Any],
    *,
    idempotency_key: str | None = None,
) -> Operation:
    """Сохранить способ оплаты для повторных списаний."""
    return Operation(
        method="POST",
        path=BASE_PATH,
        body=params,
        parse=PaymentMethod.from_api,
        idempotent=True,
        idempotency_key=idempotency_key,
    )


def get(payment_method_id: str) -> Operation:
    """Запросить сохранённый способ оплаты."""
    return Operation(
        method="GET",
        path=f"{BASE_PATH}/{payment_method_id}",
        parse=PaymentMethod.from_api,
    )
