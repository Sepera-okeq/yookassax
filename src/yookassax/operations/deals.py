"""Операции со сделками безопасной сделки: /deals."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from ..models import Deal, Page
from ..operation import Operation

__all__ = ["create", "get", "list_page"]

BASE_PATH = "/deals"


def create(
    params: Mapping[str, Any],
    *,
    idempotency_key: str | None = None,
) -> Operation:
    """Создать сделку."""
    return Operation(
        method="POST",
        path=BASE_PATH,
        body=params,
        parse=Deal.from_api,
        idempotent=True,
        idempotency_key=idempotency_key,
    )


def get(deal_id: str) -> Operation:
    """Запросить сделку."""
    return Operation(
        method="GET",
        path=f"{BASE_PATH}/{deal_id}",
        parse=Deal.from_api,
    )


def list_page(**filters: Any) -> Operation:
    """Запросить страницу списка сделок."""
    return Operation(
        method="GET",
        path=BASE_PATH,
        params=filters,
        parse=lambda payload: Page.of(Deal, payload),
    )
