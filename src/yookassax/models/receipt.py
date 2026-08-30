"""Чеки по 54-ФЗ."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, ClassVar

from .base import Model, ModelClass
from .common import Amount

__all__ = ["Receipt", "ReceiptItem"]


@dataclass(slots=True)
class ReceiptItem(Model):
    """Позиция чека."""

    description: str | None = None
    quantity: str | None = None
    amount: Amount | None = None
    vat_code: int | None = None
    payment_subject: str | None = None
    payment_mode: str | None = None
    measure: str | None = None
    country_of_origin_code: str | None = None
    customs_declaration_number: str | None = None
    excise: str | None = None
    supplier: dict[str, Any] | None = None
    agent_type: str | None = None
    product_code: str | None = None
    payment_subject_industry_details: list[dict[str, Any]] | None = None
    # Маркированные товары: код маркировки, режим и дробное количество.
    mark_code_info: dict[str, Any] | None = None
    mark_mode: str | None = None
    mark_quantity: dict[str, Any] | None = None
    planned_status: int | None = None

    nested_models: ClassVar[dict[str, ModelClass]] = {"amount": Amount}


@dataclass(slots=True)
class Receipt(Model):
    """Чек, зарегистрированный в налоговой."""

    id: str | None = None
    type: str | None = None
    payment_id: str | None = None
    refund_id: str | None = None
    status: str | None = None
    items: list[ReceiptItem] | None = None
    settlements: list[dict[str, Any]] | None = None
    registered_at: datetime | None = None
    fiscal_document_number: str | None = None
    fiscal_storage_number: str | None = None
    fiscal_attribute: str | None = None
    fiscal_provider_id: str | None = None
    receipt_registration: str | None = None
    tax_system_code: int | None = None
    on_behalf_of: str | None = None
    internet: bool | None = None
    timezone: int | None = None
    receipt_industry_details: list[dict[str, Any]] | None = None
    receipt_operational_details: dict[str, Any] | None = None

    datetime_fields: ClassVar[tuple[str, ...]] = ("registered_at",)
    nested_lists: ClassVar[dict[str, ModelClass]] = {"items": ReceiptItem}
