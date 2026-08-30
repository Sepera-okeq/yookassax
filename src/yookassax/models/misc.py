"""Остальные объекты API: счета, персональные данные, самозанятые, СБП."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, ClassVar

from .base import Model, ModelClass
from .common import CancellationDetails

__all__ = ["Invoice", "PersonalData", "PosLink", "SbpBank", "SelfEmployed"]


@dataclass(slots=True)
class Invoice(Model):
    """Счёт на оплату."""

    id: str | None = None
    status: str | None = None
    cart: list[dict[str, Any]] | None = None
    delivery_method: dict[str, Any] | None = None
    payment_details: dict[str, Any] | None = None
    created_at: datetime | None = None
    expires_at: datetime | None = None
    description: str | None = None
    cancellation_details: CancellationDetails | None = None
    metadata: dict[str, Any] | None = None

    datetime_fields: ClassVar[tuple[str, ...]] = ("created_at", "expires_at")
    nested_models: ClassVar[dict[str, ModelClass]] = {
        "cancellation_details": CancellationDetails,
    }


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
    recipient: dict[str, Any] | None = None
    payment: dict[str, Any] | None = None


@dataclass(slots=True)
class SbpBank(Model):
    """Банк из справочника СБП."""

    bank_id: str | None = None
    name: str | None = None
    bic: str | None = None
