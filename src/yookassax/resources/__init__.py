"""Ресурсы API.

Каждый ресурс существует в двух вариантах: синхронном и асинхронном. Оба
берут описания вызовов из пакета operations, поэтому поведение у них одинаковое.
"""

from .base import AsyncResource, Resource
from .deals import AsyncDeals, Deals
from .parties import (
    AsyncInvoices,
    AsyncPersonalData,
    AsyncSelfEmployed,
    Invoices,
    PersonalData,
    SelfEmployed,
)
from .payment_methods import AsyncPaymentMethods, PaymentMethods
from .payments import AsyncPayments, Payments
from .payouts import AsyncPayouts, Payouts
from .pos import AsyncPosLinks, AsyncSbpBanks, PosLinks, SbpBanks
from .receipts import AsyncReceipts, Receipts
from .refunds import AsyncRefunds, Refunds
from .shop import AsyncSettings, AsyncWebhooks, Settings, Webhooks

__all__ = [
    "AsyncDeals",
    "AsyncInvoices",
    "AsyncPaymentMethods",
    "AsyncPayments",
    "AsyncPayouts",
    "AsyncPersonalData",
    "AsyncPosLinks",
    "AsyncReceipts",
    "AsyncRefunds",
    "AsyncResource",
    "AsyncSbpBanks",
    "AsyncSelfEmployed",
    "AsyncSettings",
    "AsyncWebhooks",
    "Deals",
    "Invoices",
    "PaymentMethods",
    "Payments",
    "Payouts",
    "PersonalData",
    "PosLinks",
    "Receipts",
    "Refunds",
    "Resource",
    "SbpBanks",
    "SelfEmployed",
    "Settings",
    "Webhooks",
]
