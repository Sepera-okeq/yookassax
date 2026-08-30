"""Операции с выплатами: /payouts."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from ..models import Page, Payout
from ..operation import Operation

__all__ = ["create", "get", "list_page", "search"]

BASE_PATH = "/payouts"


def create(
    params: Mapping[str, Any],
    *,
    idempotency_key: str | None = None,
) -> Operation:
    """Создать выплату."""
    return Operation(
        method="POST",
        path=BASE_PATH,
        body=params,
        parse=Payout.from_api,
        idempotent=True,
        idempotency_key=idempotency_key,
    )


def get(payout_id: str) -> Operation:
    """Запросить состояние выплаты."""
    return Operation(
        method="GET",
        path=f"{BASE_PATH}/{payout_id}",
        parse=Payout.from_api,
    )


def list_page(**filters: Any) -> Operation:
    """Запросить страницу списка выплат."""
    return Operation(
        method="GET",
        path=BASE_PATH,
        params=filters,
        parse=lambda payload: Page.of(Payout, payload),
    )


def search(**filters: Any) -> Operation:
    """Найти выплаты по метаданным и датам.

    Отличается от list_page набором фильтров: здесь доступен поиск по
    metadata. Параметры: created_at.gte, created_at.gt, created_at.lte,
    created_at.lt, metadata, limit, cursor.
    """
    return Operation(
        method="GET",
        path=f"{BASE_PATH}/search",
        params=filters,
        parse=lambda payload: Page.of(Payout, payload),
    )
