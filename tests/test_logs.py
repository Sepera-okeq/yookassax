"""Логи обращений к API."""

from __future__ import annotations

import logging

import httpx
import pytest
import respx

from yookassax import NotFound, TransportError
from yookassax.retry import RetryPolicy

from .conftest import API_BASE_URL


@pytest.fixture
def logs(caplog):
    caplog.set_level(logging.DEBUG, logger="yookassax")
    return caplog


@respx.mock
def test_successful_request_is_logged(kassa, logs, payment_payload):
    respx.post(f"{API_BASE_URL}/payments").mock(
        return_value=httpx.Response(200, json=payment_payload)
    )

    kassa.payments.create({"amount": {"value": "100.00", "currency": "RUB"}})

    messages = [record.getMessage() for record in logs.records]
    assert any("POST" in message and "/payments" in message for message in messages)
    assert any("-> 200" in message for message in messages)


@respx.mock
def test_secret_key_never_reaches_the_log(kassa, logs, payment_payload):
    """В заголовке Authorization лежит ключ магазина, а лог живёт долго."""
    respx.post(f"{API_BASE_URL}/payments").mock(
        return_value=httpx.Response(200, json=payment_payload)
    )

    kassa.payments.create({"amount": {"value": "100.00", "currency": "RUB"}})

    written = "\n".join(record.getMessage() for record in logs.records)
    assert "test_secret" not in written
    assert "Basic " not in written
    assert "<скрыто>" in written


@respx.mock
def test_body_is_logged_only_on_debug(kassa, caplog, payment_payload):
    """На INFO тела нет: там персональные данные плательщика."""
    caplog.set_level(logging.INFO, logger="yookassax")
    respx.post(f"{API_BASE_URL}/payments").mock(
        return_value=httpx.Response(200, json=payment_payload)
    )

    kassa.payments.create({"amount": {"value": "100.00", "currency": "RUB"}})

    written = "\n".join(record.getMessage() for record in caplog.records)
    assert "тело" not in written
    assert "-> 200" in written


@respx.mock
def test_error_response_is_logged_as_warning(kassa, logs):
    respx.get(f"{API_BASE_URL}/payments/p-1").mock(
        return_value=httpx.Response(404, json={"code": "not_found", "id": "err-1"})
    )

    with pytest.raises(NotFound):
        kassa.payments.get("p-1")

    levels = {
        record.levelno
        for record in logs.records
        if "-> 404" in record.getMessage()
    }
    assert levels == {logging.WARNING}


@respx.mock
def test_retries_are_logged(kassa, logs, payment_payload):
    """Повтор должен быть виден: иначе непонятно, почему запрос шёл секунду."""
    kassa._retry = RetryPolicy(attempts=3, backoff=0.001, max_backoff=0.001)
    route = respx.post(f"{API_BASE_URL}/payments")
    route.side_effect = [
        httpx.Response(500, json={"code": "internal_server_error"}),
        httpx.Response(200, json=payment_payload),
    ]

    kassa.payments.create({"amount": {"value": "100.00", "currency": "RUB"}})

    messages = [record.getMessage() for record in logs.records]
    assert any("повтор" in message for message in messages)
    assert any("попытка 2" in message for message in messages)


@respx.mock
def test_transport_failure_is_logged(kassa, logs):
    """Ответа не было: в логе должно остаться, что состояние неизвестно."""
    kassa._retry = RetryPolicy(attempts=1, backoff=0.001, max_backoff=0.001)
    respx.post(f"{API_BASE_URL}/payments").mock(
        side_effect=httpx.ConnectError("соединение разорвано")
    )

    with pytest.raises(TransportError):
        kassa.payments.create({"amount": {"value": "100.00", "currency": "RUB"}})

    messages = [record.getMessage() for record in logs.records]
    assert any("без ответа" in message for message in messages)


def test_logger_is_quiet_without_configuration(payment_payload):
    """Без настройки логирования библиотека не пишет никуда сама."""
    logger = logging.getLogger("yookassax")

    assert not logger.handlers, "обработчик настраивает приложение, а не библиотека"
    assert logger.propagate
