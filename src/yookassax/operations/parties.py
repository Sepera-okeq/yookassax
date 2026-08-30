"""Операции с контрагентами: счета, персональные данные, самозанятые."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from ..models import Invoice, PersonalData, SelfEmployed
from ..operation import Operation

__all__ = [
    "invoice_create",
    "invoice_get",
    "personal_data_create",
    "personal_data_get",
    "self_employed_create",
    "self_employed_get",
]


def invoice_create(
    params: Mapping[str, Any],
    *,
    idempotency_key: str | None = None,
) -> Operation:
    """Выставить счёт."""
    return Operation(
        method="POST",
        path="/invoices",
        body=params,
        parse=Invoice.from_api,
        idempotent=True,
        idempotency_key=idempotency_key,
    )


def invoice_get(invoice_id: str) -> Operation:
    """Запросить счёт."""
    return Operation(
        method="GET",
        path=f"/invoices/{invoice_id}",
        parse=Invoice.from_api,
    )


def personal_data_create(
    params: Mapping[str, Any],
    *,
    idempotency_key: str | None = None,
) -> Operation:
    """Передать персональные данные получателя выплаты."""
    return Operation(
        method="POST",
        path="/personal_data",
        body=params,
        parse=PersonalData.from_api,
        idempotent=True,
        idempotency_key=idempotency_key,
    )


def personal_data_get(personal_data_id: str) -> Operation:
    """Запросить состояние переданных персональных данных."""
    return Operation(
        method="GET",
        path=f"/personal_data/{personal_data_id}",
        parse=PersonalData.from_api,
    )


def self_employed_create(
    params: Mapping[str, Any],
    *,
    idempotency_key: str | None = None,
) -> Operation:
    """Зарегистрировать самозанятого.

    Эндпоинта нет в публичной спецификации OpenAPI: он относится к продукту
    выплат самозанятым и документирован отдельно. Реализован по официальному
    SDK, поэтому в тесте покрытия спеки вынесен в список исключений.
    """
    return Operation(
        method="POST",
        path="/self_employed",
        body=params,
        parse=SelfEmployed.from_api,
        idempotent=True,
        idempotency_key=idempotency_key,
    )


def self_employed_get(self_employed_id: str) -> Operation:
    """Запросить состояние регистрации самозанятого."""
    return Operation(
        method="GET",
        path=f"/self_employed/{self_employed_id}",
        parse=SelfEmployed.from_api,
    )
