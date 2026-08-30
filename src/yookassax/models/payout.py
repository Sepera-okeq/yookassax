"""Выплаты продавцам и самозанятым."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, ClassVar

from .base import Model, ModelClass
from .common import Amount, CancellationDetails
from .deal import Deal

__all__ = ["Payout"]


@dataclass(slots=True)
class Payout(Model):
    """Выплата."""

    id: str | None = None
    status: str | None = None
    amount: Amount | None = None
    payout_destination: dict[str, Any] | None = None
    description: str | None = None
    created_at: datetime | None = None
    succeeded_at: datetime | None = None
    deal: Deal | None = None
    self_employed: dict[str, Any] | None = None
    receipt: dict[str, Any] | None = None
    cancellation_details: CancellationDetails | None = None
    test: bool | None = None
    metadata: dict[str, Any] | None = None

    datetime_fields: ClassVar[tuple[str, ...]] = ("created_at", "succeeded_at")
    nested_models: ClassVar[dict[str, ModelClass]] = {
        "amount": Amount,
        "deal": Deal,
        "cancellation_details": CancellationDetails,
    }

    @property
    def is_succeeded(self) -> bool:
        """Выплата дошла до получателя."""
        return self.status == "succeeded"
