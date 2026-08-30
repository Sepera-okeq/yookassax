"""Поведение синхронного клиента."""

from __future__ import annotations

import httpx
import pytest
import respx

from yookassax import BadRequest, Forbidden, NotFound, TransportError

from .conftest import API_BASE_URL

SUCCEEDED = {
    "id": "p1",
    "status": "succeeded",
    "amount": {"value": "10.00", "currency": "RUB"},
}


@respx.mock(base_url=API_BASE_URL)
def test_create_payment_returns_model(respx_mock, kassa, payment_payload):
    respx_mock.post("/payments").mock(
        return_value=httpx.Response(200, json=payment_payload)
    )

    payment = kassa.payments.create({"amount": {"value": "100.00", "currency": "RUB"}})

    assert payment.id == payment_payload["id"]
    assert payment.is_pending


@respx.mock(base_url=API_BASE_URL)
def test_idempotency_key_is_added_automatically(respx_mock, kassa):
    """Без ключа повтор после обрыва создал бы второй платёж."""
    route = respx_mock.post("/payments").mock(
        return_value=httpx.Response(200, json=SUCCEEDED)
    )

    kassa.payments.create({"amount": {"value": "10.00", "currency": "RUB"}})

    assert "Idempotence-Key" in route.calls.last.request.headers


@respx.mock(base_url=API_BASE_URL)
def test_custom_idempotency_key_is_used(respx_mock, kassa):
    route = respx_mock.post("/payments").mock(
        return_value=httpx.Response(200, json=SUCCEEDED)
    )

    kassa.payments.create({"amount": {}}, idempotency_key="order-42")

    assert route.calls.last.request.headers["Idempotence-Key"] == "order-42"


@respx.mock(base_url=API_BASE_URL)
def test_get_request_has_no_idempotency_key(respx_mock, kassa):
    """GET ничего не меняет, ключ идемпотентности ему не нужен."""
    route = respx_mock.get("/payments/p1").mock(
        return_value=httpx.Response(200, json=SUCCEEDED)
    )

    kassa.payments.get("p1")

    assert "Idempotence-Key" not in route.calls.last.request.headers


@respx.mock(base_url=API_BASE_URL)
def test_status_202_is_retried(respx_mock, kassa):
    """202 означает, что ЮKassa ещё считает, и просит повторить запрос."""
    route = respx_mock.get("/payments/p1").mock(
        side_effect=[
            httpx.Response(202, json={}),
            httpx.Response(202, json={}),
            httpx.Response(200, json=SUCCEEDED),
        ]
    )

    payment = kassa.payments.get("p1")

    assert route.call_count == 3
    assert payment.is_succeeded


@respx.mock(base_url=API_BASE_URL)
def test_client_error_is_not_retried(respx_mock, kassa):
    """На 400 второй запрос даст тот же ответ, повторять бессмысленно."""
    route = respx_mock.post("/payments").mock(
        return_value=httpx.Response(
            400,
            json={
                "code": "invalid_request",
                "description": "Сумма меньше минимальной",
                "parameter": "amount",
            },
        )
    )

    with pytest.raises(BadRequest) as exc_info:
        kassa.payments.create({})

    assert route.call_count == 1
    assert exc_info.value.code == "invalid_request"
    assert exc_info.value.parameter == "amount"


@respx.mock(base_url=API_BASE_URL)
def test_network_failure_retries_with_same_key(respx_mock, kassa):
    """Иначе повтор создал бы второй платёж."""
    route = respx_mock.post("/payments").mock(
        side_effect=[httpx.ConnectError("обрыв"), httpx.Response(200, json=SUCCEEDED)]
    )

    kassa.payments.create({"amount": {}})

    keys = [call.request.headers["Idempotence-Key"] for call in route.calls]
    assert route.call_count == 2
    assert keys[0] == keys[1]


@respx.mock(base_url=API_BASE_URL)
def test_exhausted_retries_raise_transport_error(respx_mock, kassa):
    respx_mock.post("/payments").mock(side_effect=httpx.ConnectError("обрыв"))

    with pytest.raises(TransportError):
        kassa.payments.create({"amount": {}})


@respx.mock(base_url=API_BASE_URL)
def test_status_codes_map_to_exceptions(respx_mock, kassa):
    respx_mock.get("/payments/missing").mock(
        return_value=httpx.Response(404, json={"code": "not_found"})
    )
    respx_mock.post("/payments").mock(
        return_value=httpx.Response(403, json={"code": "forbidden"})
    )

    with pytest.raises(NotFound):
        kassa.payments.get("missing")
    with pytest.raises(Forbidden):
        kassa.payments.create({})


@respx.mock(base_url=API_BASE_URL)
def test_empty_response_body_is_handled(respx_mock, kassa):
    """DELETE /webhooks отвечает без тела."""
    respx_mock.delete("/webhooks/wh-1").mock(return_value=httpx.Response(200))

    assert kassa.webhooks.remove("wh-1") is True


@respx.mock(base_url=API_BASE_URL)
def test_iterate_follows_cursors(respx_mock, kassa):
    respx_mock.get("/payments").mock(
        side_effect=[
            httpx.Response(
                200,
                json={"items": [{"id": "a"}, {"id": "b"}], "next_cursor": "cur-1"},
            ),
            httpx.Response(200, json={"items": [{"id": "c"}]}),
        ]
    )

    identifiers = [payment.id for payment in kassa.payments.iterate(limit=2)]

    assert identifiers == ["a", "b", "c"]


@respx.mock(base_url=API_BASE_URL)
def test_none_filters_are_dropped(respx_mock, kassa):
    """None-значения не должны превращаться в параметры строки запроса."""
    route = respx_mock.get("/payments").mock(
        return_value=httpx.Response(200, json={"items": []})
    )

    kassa.payments.list(status="succeeded", cursor=None)

    assert "cursor" not in route.calls.last.request.url.params
    assert route.calls.last.request.url.params["status"] == "succeeded"
