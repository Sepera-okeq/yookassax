"""Сделка безопасной сделки."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, ClassVar

from .base import Model, ModelClass
from .common import Amount

__all__ = ["Deal"]


@dataclass(slots=True)
class Deal(Model):
    """Сделка: держит деньги до выполнения обязательств продавцом."""

    id: str | None = None
    type: str | None = None
    status: str | None = None
    balance: Amount | None = None
    payout_balance: Amount | None = None
    description: str | None = None
    fee_moment: str | None = None
    created_at: datetime | None = None
    expires_at: datetime | None = None
    test: bool | None = None
    metadata: dict[str, Any] | None = None

    datetime_fields: ClassVar[tuple[str, ...]] = ("created_at", "expires_at")
    nested_models: ClassVar[dict[str, ModelClass]] = {
        "balance": Amount,
        "payout_balance": Amount,
    }
