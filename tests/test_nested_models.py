"""Вложенные объекты ответов разбираются в модели, а не в словари."""

from __future__ import annotations

import dataclasses
from decimal import Decimal

import pytest

from yookassax import models
from yookassax.models import (
    Invoice,
    Me,
    Payment,
    PaymentMethod,
    Payout,
    PosLink,
    Receipt,
    Refund,
)


def test_authorization_details_three_d_secure():
    payment = Payment.from_api(
        {"authorization_details": {"rrn": "1", "three_d_secure": {"applied": True}}}
    )

    assert payment.authorization_details.three_d_secure.applied is True


def test_payment_deal_carries_settlements():
    """В платеже приходит не сделка целиком, а её идентификатор и расчёты."""
    payment = Payment.from_api(
        {
            "deal": {
                "id": "dl-1",
                "settlements": [
                    {"type": "payout", "amount": {"value": "70.00", "currency": "RUB"}}
                ],
            }
        }
    )

    assert payment.deal.id == "dl-1"
    assert payment.deal.settlements[0].amount.value == Decimal("70.00")


def test_bank_card_product():
    method = PaymentMethod.from_api(
        {
            "type": "bank_card",
            "card": {"last4": "4444", "card_product": {"code": "MIR", "name": "Mir"}},
        }
    )

    assert method.card.card_product.name == "Mir"


def test_sbp_payer_bank_details():
    method = PaymentMethod.from_api(
        {"type": "sbp", "payer_bank_details": {"bank_id": "1crt", "bic": "044525225"}}
    )

    assert method.payer_bank_details.bic == "044525225"


def test_refund_method_and_sources():
    refund = Refund.from_api(
        {
            "sources": [
                {
                    "account_id": "1",
                    "amount": {"value": "5.00", "currency": "RUB"},
                    "platform_fee_amount": {"value": "1.00", "currency": "RUB"},
                }
            ],
            "refund_method": {"type": "sbp", "sbp_operation_id": "op-1"},
            "refund_authorization_details": {"rrn": "123"},
            "deal": {
                "id": "dl-1",
                "refund_settlements": [
                    {"type": "payout", "amount": {"value": "5.00", "currency": "RUB"}}
                ],
            },
        }
    )

    assert refund.sources[0].platform_fee_amount.value == Decimal("1.00")
    assert refund.refund_method.sbp_operation_id == "op-1"
    assert refund.refund_authorization_details.rrn == "123"
    assert refund.deal.refund_settlements[0].amount.value == Decimal("5.00")


def test_payout_destination_and_receipt():
    payout = Payout.from_api(
        {
            "payout_destination": {"type": "bank_card", "card": {"last4": "4444"}},
            "self_employed": {"id": "se-1"},
            "receipt": {
                "npd_receipt_id": "r-1",
                "amount": {"value": "100.00", "currency": "RUB"},
            },
        }
    )

    assert payout.payout_destination.card.last4 == "4444"
    assert payout.self_employed.id == "se-1"
    assert payout.receipt.amount.value == Decimal("100.00")


def test_receipt_item_marking():
    receipt = Receipt.from_api(
        {
            "items": [
                {
                    "description": "Товар",
                    "supplier": {"name": "Поставщик", "inn": "6321341814"},
                    "mark_code_info": {"gs_1m": "код"},
                    "mark_quantity": {"numerator": 1, "denominator": 2},
                    "payment_subject_industry_details": [{"federal_id": "001"}],
                }
            ],
            "settlements": [
                {"type": "cashless", "amount": {"value": "1.00", "currency": "RUB"}}
            ],
            "receipt_operational_details": {
                "operation_id": 1,
                "created_at": "2026-08-30T10:00:00.000Z",
            },
        }
    )

    item = receipt.items[0]
    assert item.supplier.inn == "6321341814"
    assert item.mark_quantity.denominator == 2
    assert item.mark_code_info.gs_1m == "код"
    assert item.payment_subject_industry_details[0].federal_id == "001"
    assert receipt.settlements[0].amount.value == Decimal("1.00")
    assert receipt.receipt_operational_details.created_at.year == 2026


def test_invoice_cart_and_delivery():
    invoice = Invoice.from_api(
        {
            "cart": [
                {
                    "description": "Товар",
                    "price": {"value": "10.00", "currency": "RUB"},
                    "quantity": 2,
                }
            ],
            "delivery_method": {"type": "self", "url": "https://yoomoney.ru/i/1"},
            "payment_details": {"id": "p-1", "status": "succeeded"},
        }
    )

    assert invoice.cart[0].price.value == Decimal("10.00")
    assert invoice.delivery_method.url.endswith("/1")
    assert invoice.payment_details.status == "succeeded"


def test_pos_link_and_shop_settings():
    link = PosLink.from_api(
        {
            "recipient": {"account_id": "123", "gateway_id": "456"},
            "payment": {"id": "p-1", "status": "succeeded"},
        }
    )
    me = Me.from_api({"fiscalization": {"enabled": True, "provider": "atol"}})

    assert link.recipient.gateway_id == "456"
    assert link.payment.status == "succeeded"
    assert me.fiscalization.provider == "atol"


MODEL_NAMES = sorted(
    name
    for name in models.__all__
    if dataclasses.is_dataclass(getattr(models, name, None))
)


@pytest.mark.parametrize("name", MODEL_NAMES)
def test_model_survives_an_empty_payload(name):
    """Пустое тело не должно ронять разбор: ЮKassa часто не шлёт лишнего."""
    getattr(models, name).from_api({})
