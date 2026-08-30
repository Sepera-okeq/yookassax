"""Остальные объекты API: счета, персональные данные, самозанятые, СБП."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, ClassVar

from .base import Model, ModelClass
from .common import Amount, CancellationDetails, Recipient

__all__ = [
    "DeliveryMethod",
    "Invoice",
    "InvoicePaymentDetails",
    "LineItem",
    "PersonalData",
    "PosLink",
    "PosLinkPayment",
    "SbpBank",
    "SelfEmployed",
]


@dataclass(slots=True)
class LineItem(Model):
    """Позиция корзины счёта."""

    description: str | None = None
    price: Amount | None = None
    discount_price: Amount | None = None
    quantity: float | None = None

    nested_models: ClassVar[dict[str, ModelClass]] = {
        "price": Amount,
        "discount_price": Amount,
    }


@dataclass(slots=True)
class DeliveryMethod(Model):
    """Способ доставки счёта плательщику.

    У типа self в url лежит ссылка, которую магазин отправляет сам.
    """

    type: str | None = None
    url: str | None = None


@dataclass(slots=True)
class InvoicePaymentDetails(Model):
    """Платёж по счёту. Появляется, когда счёт оплачен."""

    id: str | None = None
    status: str | None = None


@dataclass(slots=True)
class PosLinkPayment(Model):
    """Последний платёж по кассовой ссылке."""

    id: str | None = None
    status: str | None = None


@dataclass(slots=True)
class Invoice(Model):
    """Счёт на оплату."""

    id: str | None = None
    status: str | None = None
    cart: list[LineItem] | None = None
    delivery_method: DeliveryMethod | None = None
    payment_details: InvoicePaymentDetails | None = None
    created_at: datetime | None = None
    expires_at: datetime | None = None
    description: str | None = None
    cancellation_details: CancellationDetails | None = None
    metadata: dict[str, Any] | None = None

    datetime_fields: ClassVar[tuple[str, ...]] = ("created_at", "expires_at")
    nested_models: ClassVar[dict[str, ModelClass]] = {
        "cancellation_details": CancellationDetails,
        "delivery_method": DeliveryMethod,
        "payment_details": InvoicePaymentDetails,
    }
    nested_lists: ClassVar[dict[str, ModelClass]] = {"cart": LineItem}


@dataclass(slots=True)
class PersonalData(Model):
    """Персональные данные получателя выплаты.

    Хранятся на стороне ЮKassa и живут ограниченное время, см. expires_at.
    """

    id: str | None = None
    type: str | None = None
    status: str | None = None
    created_at: datetime | None = None
    expires_at: datetime | None = None
    cancellation_details: CancellationDetails | None = None
    metadata: dict[str, Any] | None = None

    datetime_fields: ClassVar[tuple[str, ...]] = ("created_at", "expires_at")
    nested_models: ClassVar[dict[str, ModelClass]] = {
        "cancellation_details": CancellationDetails,
    }


@dataclass(slots=True)
class SelfEmployed(Model):
    """Самозанятый получатель выплат."""

    id: str | None = None
    status: str | None = None
    itn: str | None = None
    phone: str | None = None
    confirmation: dict[str, Any] | None = None
    description: str | None = None
    created_at: datetime | None = None
    test: bool | None = None
    metadata: dict[str, Any] | None = None

    datetime_fields: ClassVar[tuple[str, ...]] = ("created_at",)


@dataclass(slots=True)
class PosLink(Model):
    """Ссылка на оплату в кассе."""

    id: str | None = None
    status: str | None = None
    type: str | None = None
    recipient: Recipient | None = None
    payment: PosLinkPayment | None = None

    nested_models: ClassVar[dict[str, ModelClass]] = {
        "recipient": Recipient,
        "payment": PosLinkPayment,
    }


@dataclass(slots=True)
class SbpBank(Model):
    """Банк из справочника СБП."""

    bank_id: str | None = None
    name: str | None = None
    bic: str | None = None
