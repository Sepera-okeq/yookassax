"""Чеки по 54-ФЗ."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import ClassVar

from .base import Model, ModelClass
from .common import Amount, Settlement

__all__ = [
    "IndustryDetails",
    "MarkCodeInfo",
    "MarkQuantity",
    "OperationalDetails",
    "Receipt",
    "ReceiptItem",
    "ReceiptItemSupplier",
]


@dataclass(slots=True)
class ReceiptItemSupplier(Model):
    """Поставщик товара или услуги (тег 1224)."""

    name: str | None = None
    phone: str | None = None
    inn: str | None = None


@dataclass(slots=True)
class IndustryDetails(Model):
    """Отраслевой реквизит (тег 1260)."""

    federal_id: str | None = None
    document_date: str | None = None
    document_number: str | None = None
    value: str | None = None


@dataclass(slots=True)
class OperationalDetails(Model):
    """Операционный реквизит чека (тег 1270)."""

    operation_id: int | None = None
    value: str | None = None
    created_at: datetime | None = None

    datetime_fields: ClassVar[tuple[str, ...]] = ("created_at",)


@dataclass(slots=True)
class MarkQuantity(Model):
    """Дробное количество маркированного товара (тег 1291)."""

    numerator: int | None = None
    denominator: int | None = None


@dataclass(slots=True)
class MarkCodeInfo(Model):
    """Код маркировки товара (тег 1163).

    Заполнено ровно одно поле - то, в каком формате пришёл код.
    """

    mark_code_raw: str | None = None
    unknown: str | None = None
    ean_8: str | None = None
    ean_13: str | None = None
    itf_14: str | None = None
    gs_10: str | None = None
    gs_1m: str | None = None
    short: str | None = None
    fur: str | None = None
    egais_20: str | None = None
    egais_30: str | None = None


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
    supplier: ReceiptItemSupplier | None = None
    agent_type: str | None = None
    product_code: str | None = None
    payment_subject_industry_details: list[IndustryDetails] | None = None
    # Маркированные товары: код маркировки, режим и дробное количество.
    mark_code_info: MarkCodeInfo | None = None
    mark_mode: str | None = None
    mark_quantity: MarkQuantity | None = None
    planned_status: int | None = None

    nested_models: ClassVar[dict[str, ModelClass]] = {
        "amount": Amount,
        "supplier": ReceiptItemSupplier,
        "mark_code_info": MarkCodeInfo,
        "mark_quantity": MarkQuantity,
    }
    nested_lists: ClassVar[dict[str, ModelClass]] = {
        "payment_subject_industry_details": IndustryDetails,
    }


@dataclass(slots=True)
class Receipt(Model):
    """Чек, зарегистрированный в налоговой."""

    id: str | None = None
    type: str | None = None
    payment_id: str | None = None
    refund_id: str | None = None
    status: str | None = None
    items: list[ReceiptItem] | None = None
    settlements: list[Settlement] | None = None
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
    receipt_industry_details: list[IndustryDetails] | None = None
    receipt_operational_details: OperationalDetails | None = None

    datetime_fields: ClassVar[tuple[str, ...]] = ("registered_at",)
    nested_models: ClassVar[dict[str, ModelClass]] = {
        "receipt_operational_details": OperationalDetails,
    }
    nested_lists: ClassVar[dict[str, ModelClass]] = {
        "items": ReceiptItem,
        "settlements": Settlement,
        "receipt_industry_details": IndustryDetails,
    }
