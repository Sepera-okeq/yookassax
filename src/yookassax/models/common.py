"""Вложенные объекты, общие для нескольких ресурсов."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Any, ClassVar

from .base import Model, ModelClass

__all__ = [
    "Amount",
    "AuthorizationDetails",
    "CancellationDetails",
    "Confirmation",
    "Recipient",
    "Transfer",
]


@dataclass(slots=True)
class Amount(Model):
    """Сумма и валюта.

    Значение разбирается в Decimal, а не в float: на деньгах двоичная дробь
    накапливает погрешность.
    """

    value: Decimal | None = None
    currency: str | None = None

    decimal_fields: ClassVar[tuple[str, ...]] = ("value",)

    def __str__(self) -> str:
        return f"{self.value} {self.currency}"


@dataclass(slots=True)
class Confirmation(Model):
    """Сценарий подтверждения: как довести плательщика до оплаты.

    Тип redirect ведёт на страницу оплаты, embedded отдаёт токен для виджета,
    qr - строку для кода.
    """

    type: str | None = None
    confirmation_url: str | None = None
    confirmation_token: str | None = None
    confirmation_data: str | None = None
    return_url: str | None = None
    enforce: bool | None = None


@dataclass(slots=True)
class Recipient(Model):
    """Получатель платежа: магазин и шлюз."""

    account_id: str | None = None
    gateway_id: str | None = None


@dataclass(slots=True)
class CancellationDetails(Model):
    """Кто и почему отменил операцию.

    Поле party принимает значения yoo_money, payment_network и merchant. По
    нему видно, отменил платёж магазин, платёжная система или сама ЮKassa.
    """

    party: str | None = None
    reason: str | None = None


@dataclass(slots=True)
class AuthorizationDetails(Model):
    """Данные авторизации карточного платежа."""

    rrn: str | None = None
    auth_code: str | None = None
    three_d_secure: dict[str, Any] | None = None


@dataclass(slots=True)
class Transfer(Model):
    """Часть платежа, уходящая отдельному продавцу в маркетплейсе."""

    account_id: str | None = None
    amount: Amount | None = None
    status: str | None = None
    platform_fee_amount: Amount | None = None
    description: str | None = None
    metadata: dict[str, Any] | None = None
    release_funds: bool | None = None
    connected_account_id: str | None = None

    nested_models: ClassVar[dict[str, ModelClass]] = {
        "amount": Amount,
        "platform_fee_amount": Amount,
    }
