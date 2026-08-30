"""Возврат по платежу."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, ClassVar

from .base import Model, ModelClass
from .common import Amount, CancellationDetails, Settlement

__all__ = [
    "ElectronicCertificateRefundArticle",
    "ElectronicCertificateRefundData",
    "Refund",
    "RefundAuthorizationDetails",
    "RefundDealInfo",
    "RefundMethod",
    "RefundSource",
]


@dataclass(slots=True)
class RefundSource(Model):
    """С какого магазина и сколько удержать при возврате в маркетплейсе."""

    account_id: str | None = None
    amount: Amount | None = None
    platform_fee_amount: Amount | None = None

    nested_models: ClassVar[dict[str, ModelClass]] = {
        "amount": Amount,
        "platform_fee_amount": Amount,
    }


@dataclass(slots=True)
class RefundAuthorizationDetails(Model):
    """Данные авторизации возврата."""

    rrn: str | None = None


@dataclass(slots=True)
class ElectronicCertificateRefundArticle(Model):
    """Позиция корзины возврата на электронный сертификат."""

    article_number: int | None = None
    payment_article_number: int | None = None
    tru_code: str | None = None
    quantity: int | None = None


@dataclass(slots=True)
class ElectronicCertificateRefundData(Model):
    """Данные ФЭС НСПК для возврата на электронный сертификат."""

    amount: Amount | None = None
    basket_id: str | None = None

    nested_models: ClassVar[dict[str, ModelClass]] = {"amount": Amount}


@dataclass(slots=True)
class RefundMethod(Model):
    """Детали возврата: зависят от способа, которым платили.

    У возврата через СБП заполнен sbp_operation_id, у возврата на электронный
    сертификат - articles и electronic_certificate.
    """

    type: str | None = None
    sbp_operation_id: str | None = None
    articles: list[ElectronicCertificateRefundArticle] | None = None
    electronic_certificate: ElectronicCertificateRefundData | None = None

    nested_models: ClassVar[dict[str, ModelClass]] = {
        "electronic_certificate": ElectronicCertificateRefundData,
    }
    nested_lists: ClassVar[dict[str, ModelClass]] = {
        "articles": ElectronicCertificateRefundArticle,
    }


@dataclass(slots=True)
class RefundDealInfo(Model):
    """Сделка, в составе которой идёт возврат."""

    id: str | None = None
    refund_settlements: list[Settlement] | None = None

    nested_lists: ClassVar[dict[str, ModelClass]] = {"refund_settlements": Settlement}


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
    sources: list[RefundSource] | None = None
    deal: RefundDealInfo | None = None
    refund_method: RefundMethod | None = None
    refund_authorization_details: RefundAuthorizationDetails | None = None
    metadata: dict[str, Any] | None = None

    datetime_fields: ClassVar[tuple[str, ...]] = ("created_at",)
    nested_models: ClassVar[dict[str, ModelClass]] = {
        "amount": Amount,
        "cancellation_details": CancellationDetails,
        "deal": RefundDealInfo,
        "refund_method": RefundMethod,
        "refund_authorization_details": RefundAuthorizationDetails,
    }
    nested_lists: ClassVar[dict[str, ModelClass]] = {"sources": RefundSource}

    @property
    def is_succeeded(self) -> bool:
        """Возврат прошёл, деньги ушли плательщику."""
        return self.status == "succeeded"

    @property
    def is_canceled(self) -> bool:
        """Возврат отклонён."""
        return self.status == "canceled"
