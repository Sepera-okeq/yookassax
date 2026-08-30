"""Вложенные объекты, общие для нескольких ресурсов."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Any, ClassVar

from .base import Model, ModelClass

__all__ = [
    "Amount",
    "AuthorizationDetails",
    "BankCardData",
    "BankCardProduct",
    "CancellationDetails",
    "Confirmation",
    "PayerBankDetails",
    "Recipient",
    "Settlement",
    "ThreeDSecureDetails",
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
class ThreeDSecureDetails(Model):
    """Прошла ли аутентификация 3-D Secure."""

    applied: bool | None = None


@dataclass(slots=True)
class BankCardProduct(Model):
    """Карточный продукт платёжной системы, например Mir Supreme."""

    code: str | None = None
    name: str | None = None


@dataclass(slots=True)
class BankCardData(Model):
    """Данные банковской карты.

    Номер карты целиком не приходит никогда: только первые шесть и последние
    четыре цифры.
    """

    first6: str | None = None
    last4: str | None = None
    expiry_month: str | None = None
    expiry_year: str | None = None
    card_type: str | None = None
    card_product: BankCardProduct | None = None
    issuer_country: str | None = None
    issuer_name: str | None = None
    source: str | None = None

    nested_models: ClassVar[dict[str, ModelClass]] = {"card_product": BankCardProduct}


@dataclass(slots=True)
class PayerBankDetails(Model):
    """Реквизиты счёта плательщика.

    Набор полей зависит от способа оплаты: у СБП это bank_id и bic, у оплаты
    по счёту от юридического лица - полные банковские реквизиты.
    """

    bank_id: str | None = None
    bic: str | None = None
    account: str | None = None
    bank_bik: str | None = None
    bank_branch: str | None = None
    bank_name: str | None = None
    full_name: str | None = None
    short_name: str | None = None
    address: str | None = None
    inn: str | None = None
    kpp: str | None = None


@dataclass(slots=True)
class Settlement(Model):
    """Расчёт: сколько и на что распределено внутри операции."""

    type: str | None = None
    amount: Amount | None = None

    nested_models: ClassVar[dict[str, ModelClass]] = {"amount": Amount}


@dataclass(slots=True)
class AuthorizationDetails(Model):
    """Данные авторизации карточного платежа."""

    rrn: str | None = None
    auth_code: str | None = None
    three_d_secure: ThreeDSecureDetails | None = None

    nested_models: ClassVar[dict[str, ModelClass]] = {
        "three_d_secure": ThreeDSecureDetails,
    }


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
