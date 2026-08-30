"""Платёж: центральный объект API."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, ClassVar

from .base import Model, ModelClass
from .common import (
    Amount,
    AuthorizationDetails,
    CancellationDetails,
    Confirmation,
    Recipient,
    Transfer,
)
from .deal import Deal

__all__ = ["InvoiceDetails", "Payment", "PaymentMethod"]


@dataclass(slots=True)
class PaymentMethod(Model):
    """Способ оплаты.

    Если saved равно True, по этому способу можно списывать повторно, передав
    его идентификатор в payment_method_id при создании нового платежа.
    """

    id: str | None = None
    type: str | None = None
    saved: bool | None = None
    status: str | None = None
    title: str | None = None
    card: dict[str, Any] | None = None
    account_number: str | None = None
    login: str | None = None
    phone: str | None = None
    payer_bank_details: dict[str, Any] | None = None
    sbp_operation_id: str | None = None


@dataclass(slots=True)
class InvoiceDetails(Model):
    """Ссылка на счёт, по которому прошёл платёж."""

    id: str | None = None


@dataclass(slots=True)
class Payment(Model):
    """Платёж."""

    id: str | None = None
    status: str | None = None
    amount: Amount | None = None
    income_amount: Amount | None = None
    refunded_amount: Amount | None = None
    description: str | None = None
    recipient: Recipient | None = None
    payment_method: PaymentMethod | None = None
    confirmation: Confirmation | None = None
    cancellation_details: CancellationDetails | None = None
    authorization_details: AuthorizationDetails | None = None
    transfers: list[Transfer] | None = None
    deal: Deal | None = None
    invoice_details: InvoiceDetails | None = None
    created_at: datetime | None = None
    captured_at: datetime | None = None
    expires_at: datetime | None = None
    paid: bool | None = None
    refundable: bool | None = None
    test: bool | None = None
    receipt_registration: str | None = None
    merchant_customer_id: str | None = None
    metadata: dict[str, Any] | None = None

    datetime_fields: ClassVar[tuple[str, ...]] = (
        "created_at",
        "captured_at",
        "expires_at",
    )
    nested_models: ClassVar[dict[str, ModelClass]] = {
        "amount": Amount,
        "income_amount": Amount,
        "refunded_amount": Amount,
        "recipient": Recipient,
        "payment_method": PaymentMethod,
        "confirmation": Confirmation,
        "cancellation_details": CancellationDetails,
        "authorization_details": AuthorizationDetails,
        "deal": Deal,
        "invoice_details": InvoiceDetails,
    }
    nested_lists: ClassVar[dict[str, ModelClass]] = {"transfers": Transfer}

    @property
    def is_succeeded(self) -> bool:
        """Платёж прошёл, деньги у магазина."""
        return self.status == "succeeded"

    @property
    def is_pending(self) -> bool:
        """Платёж создан, плательщик ещё не завершил оплату."""
        return self.status == "pending"

    @property
    def is_waiting_for_capture(self) -> bool:
        """Деньги захолдированы, нужен вызов capture или cancel."""
        return self.status == "waiting_for_capture"

    @property
    def is_canceled(self) -> bool:
        """Платёж отменён, деньги у плательщика."""
        return self.status == "canceled"

    @property
    def confirmation_url(self) -> str | None:
        """Ссылка, куда вести плательщика.

        Возвращает None, если сценарий подтверждения не предполагает редиректа,
        например для виджета или списания по сохранённому способу.
        """
        if self.confirmation is None:
            return None
        return self.confirmation.confirmation_url
