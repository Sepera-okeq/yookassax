"""Выплаты продавцам и самозанятым."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, ClassVar

from .base import Model, ModelClass
from .common import Amount, CancellationDetails

__all__ = [
    "IncomeReceipt",
    "Payout",
    "PayoutCardData",
    "PayoutDealInfo",
    "PayoutDestination",
    "PayoutSelfEmployedInfo",
]


@dataclass(slots=True)
class PayoutCardData(Model):
    """Карта, на которую ушла выплата."""

    first6: str | None = None
    last4: str | None = None
    card_type: str | None = None
    issuer_country: str | None = None
    issuer_name: str | None = None


@dataclass(slots=True)
class PayoutDestination(Model):
    """Куда ушла выплата.

    Набор полей зависит от type: bank_card заполняет card, sbp - bank_id и
    phone, yoo_money - account_number.
    """

    type: str | None = None
    card: PayoutCardData | None = None
    bank_id: str | None = None
    phone: str | None = None
    recipient_checked: bool | None = None
    sbp_operation_id: str | None = None
    account_number: str | None = None

    nested_models: ClassVar[dict[str, ModelClass]] = {"card": PayoutCardData}


@dataclass(slots=True)
class PayoutSelfEmployedInfo(Model):
    """Самозанятый, получивший выплату."""

    id: str | None = None


@dataclass(slots=True)
class PayoutDealInfo(Model):
    """Сделка, в рамках которой проведена выплата."""

    id: str | None = None


@dataclass(slots=True)
class IncomeReceipt(Model):
    """Чек самозанятого, зарегистрированный в налоговой."""

    npd_receipt_id: str | None = None
    service_name: str | None = None
    amount: Amount | None = None
    url: str | None = None

    nested_models: ClassVar[dict[str, ModelClass]] = {"amount": Amount}


@dataclass(slots=True)
class Payout(Model):
    """Выплата."""

    id: str | None = None
    status: str | None = None
    amount: Amount | None = None
    payout_destination: PayoutDestination | None = None
    description: str | None = None
    created_at: datetime | None = None
    succeeded_at: datetime | None = None
    deal: PayoutDealInfo | None = None
    self_employed: PayoutSelfEmployedInfo | None = None
    receipt: IncomeReceipt | None = None
    cancellation_details: CancellationDetails | None = None
    test: bool | None = None
    metadata: dict[str, Any] | None = None

    datetime_fields: ClassVar[tuple[str, ...]] = ("created_at", "succeeded_at")
    nested_models: ClassVar[dict[str, ModelClass]] = {
        "amount": Amount,
        "deal": PayoutDealInfo,
        "cancellation_details": CancellationDetails,
        "payout_destination": PayoutDestination,
        "self_employed": PayoutSelfEmployedInfo,
        "receipt": IncomeReceipt,
    }

    @property
    def is_succeeded(self) -> bool:
        """Выплата дошла до получателя."""
        return self.status == "succeeded"
