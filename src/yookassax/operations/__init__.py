"""Каталог операций API.

Каждая функция описывает один вызов: метод, путь, тело и способ разбора
ответа. Ни синхронный, ни асинхронный клиент своей логики не имеют, оба берут
описание отсюда. Новый эндпоинт достаточно добавить в этот пакет, и он станет
доступен сразу в обоих режимах.
"""

from . import (
    deals,
    parties,
    payment_methods,
    payments,
    payouts,
    pos,
    receipts,
    refunds,
    shop,
)

__all__ = [
    "deals",
    "parties",
    "payment_methods",
    "payments",
    "payouts",
    "pos",
    "receipts",
    "refunds",
    "shop",
]
