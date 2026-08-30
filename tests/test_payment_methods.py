"""Разбор способов оплаты по значению type."""

from __future__ import annotations

import warnings
from decimal import Decimal

import pytest

from yookassax import (
    Payment,
    PaymentMethod,
    PaymentMethodB2bSberbank,
    PaymentMethodBankCard,
    PaymentMethodElectronicCertificate,
    PaymentMethodSberLoan,
    UnknownFieldWarning,
)
from yookassax.models import PAYMENT_METHOD_MODELS


def test_type_selects_the_model():
    method = PaymentMethod.from_api({"type": "bank_card", "card": {"last4": "4444"}})

    assert isinstance(method, PaymentMethodBankCard)
    assert method.card.last4 == "4444"


def test_every_registered_type_builds_its_model():
    for type_name, model in PAYMENT_METHOD_MODELS.items():
        method = PaymentMethod.from_api({"type": type_name, "id": "pm-1"})

        assert isinstance(method, model), type_name
        assert method.type == type_name


def test_unknown_type_falls_back_to_the_base_model():
    """Новый способ оплаты не должен ронять разбор платежа."""
    method = PaymentMethod.from_api({"type": "способ_из_будущего", "id": "pm-1"})

    assert type(method) is PaymentMethod
    assert method.type == "способ_из_будущего"


def test_sber_loan_fields():
    method = PaymentMethod.from_api(
        {
            "type": "sber_loan",
            "loan_option": "installments_3",
            "discount_amount": {"value": "10.00", "currency": "RUB"},
            "suspended_until": "2026-09-01T00:00:00.000Z",
        }
    )

    assert isinstance(method, PaymentMethodSberLoan)
    assert method.loan_option == "installments_3"
    assert method.discount_amount.value == Decimal("10.00")
    assert method.suspended_until.year == 2026


def test_electronic_certificate_fields():
    method = PaymentMethod.from_api(
        {
            "type": "electronic_certificate",
            "card": {"first6": "220220", "last4": "4444"},
            "electronic_certificate": {"amount": {"value": "1.00", "currency": "RUB"}},
            "articles": [{"article_number": 1, "tru_code": "1234567890"}],
        }
    )

    assert isinstance(method, PaymentMethodElectronicCertificate)
    assert method.articles[0].tru_code == "1234567890"
    assert method.electronic_certificate.amount.value == Decimal("1.00")


def test_b2b_sberbank_fields():
    method = PaymentMethod.from_api(
        {
            "type": "b2b_sberbank",
            "payment_purpose": "Оплата по счёту 42",
            "vat_data": {"type": "calculated", "rate": "20"},
        }
    )

    assert isinstance(method, PaymentMethodB2bSberbank)
    assert method.payment_purpose == "Оплата по счёту 42"
    assert method.vat_data.rate == "20"


def test_typed_fields_do_not_warn():
    """Поля конкретного типа документированы, предупреждать о них нельзя.

    Иначе UnknownFieldWarning срабатывает на штатном ответе, и его заглушат
    фильтром вместе с настоящими новыми полями.
    """
    with warnings.catch_warnings():
        warnings.simplefilter("error", UnknownFieldWarning)
        PaymentMethod.from_api(
            {
                "type": "sber_loan",
                "id": "pm-1",
                "saved": False,
                "status": "active",
                "title": "Кредит",
                "loan_option": "loan",
                "discount_amount": {"value": "1.00", "currency": "RUB"},
                "suspended_until": "2026-09-01T00:00:00.000Z",
            }
        )


def test_payment_carries_the_typed_method():
    """Внутри платежа способ оплаты тоже разбирается по типу."""
    payment = Payment.from_api(
        {
            "id": "p-1",
            "payment_method": {"type": "b2b_sberbank", "payment_purpose": "Счёт 1"},
        }
    )

    assert isinstance(payment.payment_method, PaymentMethodB2bSberbank)
    assert payment.payment_method.payment_purpose == "Счёт 1"


@pytest.mark.parametrize("type_name", sorted(PAYMENT_METHOD_MODELS))
def test_model_name_matches_the_type(type_name):
    """Имена моделей совпадают со схемами спецификации, это держит сверку."""
    assert PAYMENT_METHOD_MODELS[type_name].__name__.startswith("PaymentMethod")


def test_holder_is_a_model():
    """holder это магазин, для которого сохраняется способ оплаты."""
    method = PaymentMethod.from_api(
        {
            "type": "bank_card",
            "holder": {"account_id": "123", "gateway_id": "456"},
        }
    )

    assert method.holder.account_id == "123"
    assert method.holder.gateway_id == "456"


def test_all_documented_payment_method_types_are_known():
    """19 типов из объекта платежа в документации ЮKassa."""
    documented = {
        "bank_card", "yoo_money", "sberbank", "tinkoff_bank", "alfabank",
        "alfa_pay", "sbp", "cash", "mobile_balance", "qiwi", "webmoney",
        "wechat", "apple_pay", "google_pay", "installments", "sber_bnpl",
        "b2b_sberbank", "sber_loan", "electronic_certificate",
    }

    assert set(PAYMENT_METHOD_MODELS) == documented
