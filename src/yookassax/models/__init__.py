"""Типизированные модели ответов ЮKassa.

Все модели наследуют Model и собираются методом from_api. Поля, которых нет в
модели, не теряются: они остаются в словаре raw и доступны через метод extra.
"""

from .base import Model, parse_datetime, parse_decimal
from .common import (
    Amount,
    AuthorizationDetails,
    CancellationDetails,
    Confirmation,
    Recipient,
    Transfer,
)
from .deal import Deal
from .misc import Invoice, PersonalData, PosLink, SbpBank, SelfEmployed
from .page import Page
from .payment import InvoiceDetails, Payment, PaymentMethod
from .payout import Payout
from .receipt import Receipt, ReceiptItem
from .refund import Refund
from .shop import Me, Webhook

__all__ = [
    "Amount",
    "AuthorizationDetails",
    "CancellationDetails",
    "Confirmation",
    "Deal",
    "Invoice",
    "InvoiceDetails",
    "Me",
    "Model",
    "Page",
    "Payment",
    "PaymentMethod",
    "Payout",
    "PersonalData",
    "PosLink",
    "Receipt",
    "ReceiptItem",
    "Recipient",
    "Refund",
    "SbpBank",
    "SelfEmployed",
    "Transfer",
    "Webhook",
    "parse_datetime",
    "parse_decimal",
]
