"""Разбор моделей."""

from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal

from yookassax import Payment
from yookassax.models import Page, parse_datetime, parse_decimal


def test_amount_is_parsed_as_decimal():
    """На деньгах float недопустим: двоичная дробь копит погрешность."""
    payment = Payment.from_api({"amount": {"value": "100.55", "currency": "RUB"}})

    assert isinstance(payment.amount.value, Decimal)
    assert payment.amount.value == Decimal("100.55")


def test_decimal_addition_is_exact():
    first = parse_decimal("0.1")
    second = parse_decimal("0.2")

    assert first + second == Decimal("0.3")


def test_zulu_datetime_is_parsed():
    """API отдаёт время с Z, до Python 3.11 fromisoformat такое не понимает."""
    value = parse_datetime("2026-08-30T10:00:00.000Z")

    assert value == datetime(2026, 8, 30, 10, 0, tzinfo=timezone.utc)


def test_unparsable_datetime_returns_none():
    assert parse_datetime("не дата") is None
    assert parse_datetime(None) is None
    assert parse_datetime("") is None


def test_unknown_fields_are_preserved(payment_payload):
    """ЮKassa добавляет поля в ответы, и это не повод отказать в обслуживании."""
    payment = Payment.from_api(payment_payload)

    assert payment.id == payment_payload["id"]
    assert payment.extra("field_from_the_future") == "значение"


def test_nested_models_are_built(payment_payload):
    payment = Payment.from_api(payment_payload)

    assert payment.confirmation.type == "redirect"
    assert payment.confirmation_url == "https://yoomoney.ru/checkout/123"


def test_confirmation_url_is_none_without_confirmation():
    """Списание по сохранённому способу идёт без редиректа."""
    payment = Payment.from_api({"id": "p1", "status": "succeeded"})

    assert payment.confirmation_url is None


def test_status_properties():
    assert Payment.from_api({"status": "succeeded"}).is_succeeded
    assert Payment.from_api({"status": "pending"}).is_pending
    assert Payment.from_api({"status": "canceled"}).is_canceled
    assert Payment.from_api({"status": "waiting_for_capture"}).is_waiting_for_capture


def test_page_iterates_and_reports_next():
    page = Page.of(
        Payment,
        {"type": "list", "items": [{"id": "a"}, {"id": "b"}], "next_cursor": "cur"},
    )

    assert len(page) == 2
    assert [item.id for item in page] == ["a", "b"]
    assert page.has_more is True


def test_page_without_cursor_is_last():
    page = Page.of(Payment, {"items": [{"id": "a"}]})

    assert page.has_more is False


def test_empty_page_is_falsy():
    assert not Page.of(Payment, {"items": []})
