"""Возврат по платежу."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, ClassVar

from .base import Model, ModelClass
from .common import Amount, CancellationDetails
from .deal import Deal

__all__ = ["Refund"]


@dataclass(slots=True)
class Refund(Model):
    """Возврат денег плательщику."""

    id: str | None = None
    payment_id: str | None = None
    status: str | None = None
    amount: Amount | None = None
    description: str | None = None
    created_at: datetime | None = None
    cancellation_details: CancellationDetails | None = None
    receipt_registration: str | None = None
    sources: list[dict[str, Any]] | None = None
    deal: Deal | None = None
    refund_method: dict[str, Any] | None = None
    refund_authorization_details: dict[str, Any] | None = None
    metadata: dict[str, Any] | None = None

    datetime_fields: ClassVar[tuple[str, ...]] = ("created_at",)
    nested_models: ClassVar[dict[str, ModelClass]] = {
        "amount": Amount,
        "cancellation_details": CancellationDetails,
        "deal": Deal,
    }

    @property
    def is_succeeded(self) -> bool:
        """Возврат прошёл, деньги ушли плательщику."""
        return self.status == "succeeded"

    @property
    def is_canceled(self) -> bool:
        """Возврат отклонён."""
        return self.status == "canceled"
