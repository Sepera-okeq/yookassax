"""Разбор уведомлений и проверка источника."""

from __future__ import annotations

import pytest

from yookassax import Payment, Refund, webhooks

PAYMENT_SUCCEEDED = {
    "type": "notification",
    "event": "payment.succeeded",
    "object": {
        "id": "22e12f66-000f-5000-8000-18db351245c7",
        "status": "succeeded",
        "amount": {"value": "100.00", "currency": "RUB"},
        "paid": True,
    },
}


def test_payment_notification_is_parsed():
    notification = webhooks.parse(PAYMENT_SUCCEEDED)

    assert notification.event == "payment.succeeded"
    assert notification.object_type == "payment"
    assert isinstance(notification.object, Payment)
    assert notification.object.is_succeeded
    assert notification.is_payment_succeeded


def test_refund_notification_is_parsed():
    notification = webhooks.parse(
        {"event": "refund.succeeded", "object": {"id": "r1", "status": "succeeded"}}
    )

    assert isinstance(notification.object, Refund)
    assert notification.is_refund_succeeded


def test_unknown_event_does_not_break_parsing():
    """Отказ обработать уведомление приводит к бесконечным повторам от ЮKassa."""
    notification = webhooks.parse(
        {"event": "something.new", "object": {"id": "x", "field": 1}}
    )

    assert notification.event == "something.new"
    assert notification.object == {"id": "x", "field": 1}


def test_empty_notification_body_is_handled():
    notification = webhooks.parse({})

    assert notification.event == ""
    assert notification.object is None


@pytest.mark.parametrize(
    "ip",
    ["185.71.76.1", "185.71.77.10", "77.75.153.5", "77.75.156.11", "77.75.154.200"],
)
def test_yookassa_addresses_are_trusted(ip):
    assert webhooks.is_trusted_ip(ip) is True


@pytest.mark.parametrize("ip", ["8.8.8.8", "192.168.0.1", "77.75.156.12", ""])
def test_foreign_addresses_are_not_trusted(ip):
    assert webhooks.is_trusted_ip(ip) is False


def test_malformed_address_is_not_trusted():
    """Неразбираемое значение должно давать отказ, а не исключение."""
    assert webhooks.is_trusted_ip("не адрес") is False
    assert webhooks.is_trusted_ip("999.999.999.999") is False


def test_address_with_whitespace_is_parsed():
    """Заголовки нередко приходят с лишними пробелами."""
    assert webhooks.is_trusted_ip("  185.71.76.1  ") is True


def test_payment_method_active_is_parsed():
    """Привязка на нулевую сумму: объект уведомления это способ оплаты."""
    notification = webhooks.parse(
        {
            "type": "notification",
            "event": "payment_method.active",
            "object": {
                "type": "bank_card",
                "id": "pm-1",
                "status": "active",
                "saved": True,
                "card": {"last4": "4444"},
            },
        }
    )

    assert notification.is_payment_method_active
    assert notification.object_type == "payment_method"
    assert notification.object.card.last4 == "4444"


def test_all_documented_events_are_known():
    """Список событий должен совпадать с документацией ЮKassa."""
    documented = {
        "payment.waiting_for_capture",
        "payment.succeeded",
        "payment.canceled",
        "refund.succeeded",
        "payout.succeeded",
        "payout.canceled",
        "deal.closed",
        "payment_method.active",
    }

    assert set(webhooks.EVENTS) == documented


def test_documented_notification_source_networks():
    """Сети отправителя из документации ЮKassa."""
    trusted = ("185.71.76.1", "185.71.77.1", "77.75.153.1", "77.75.156.11",
               "77.75.156.35", "77.75.154.200", "2a02:5180::1")
    for ip in trusted:
        assert webhooks.is_trusted_ip(ip), ip

    for ip in ("77.75.156.12", "8.8.8.8", "185.71.78.1", "не адрес", ""):
        assert not webhooks.is_trusted_ip(ip), ip
