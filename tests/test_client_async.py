"""Асинхронный клиент ведёт себя так же, как синхронный."""

from __future__ import annotations

import httpx
import pytest
import respx

from yookassax import BadRequest

from .conftest import API_BASE_URL

SUCCEEDED = {
    "id": "p1",
    "status": "succeeded",
    "amount": {"value": "10.00", "currency": "RUB"},
}


@respx.mock(base_url=API_BASE_URL)
async def test_create_payment(respx_mock, async_kassa, payment_payload):
    respx_mock.post("/payments").mock(
        return_value=httpx.Response(200, json=payment_payload)
    )

    payment = await async_kassa.payments.create({"amount": {}})

    assert payment.id == payment_payload["id"]
    assert payment.confirmation_url == "https://yoomoney.ru/checkout/123"


@respx.mock(base_url=API_BASE_URL)
async def test_idempotency_key_is_added_automatically(respx_mock, async_kassa):
    route = respx_mock.post("/payments").mock(
        return_value=httpx.Response(200, json=SUCCEEDED)
    )

    await async_kassa.payments.create({"amount": {}})

    assert "Idempotence-Key" in route.calls.last.request.headers


@respx.mock(base_url=API_BASE_URL)
async def test_status_202_is_retried(respx_mock, async_kassa):
    route = respx_mock.get("/payments/p1").mock(
        side_effect=[
            httpx.Response(202, json={}),
            httpx.Response(200, json=SUCCEEDED),
        ]
    )

    payment = await async_kassa.payments.get("p1")

    assert route.call_count == 2
    assert payment.is_succeeded


@respx.mock(base_url=API_BASE_URL)
async def test_client_error_is_not_retried(respx_mock, async_kassa):
    route = respx_mock.post("/payments").mock(
        return_value=httpx.Response(400, json={"code": "invalid_request"})
    )

    with pytest.raises(BadRequest):
        await async_kassa.payments.create({})

    assert route.call_count == 1


@respx.mock(base_url=API_BASE_URL)
async def test_iterate_follows_cursors(respx_mock, async_kassa):
    respx_mock.get("/payments").mock(
        side_effect=[
            httpx.Response(200, json={"items": [{"id": "a"}], "next_cursor": "c1"}),
            httpx.Response(200, json={"items": [{"id": "b"}]}),
        ]
    )

    identifiers = [payment.id async for payment in async_kassa.payments.iterate()]

    assert identifiers == ["a", "b"]


async def test_sync_and_async_expose_same_methods(kassa, async_kassa):
    """Режимы обязаны предоставлять одно и то же, иначе они разъедутся."""
    def public_names(resource):
        return {
            name
            for name in dir(resource)
            if not name.startswith("_") and callable(getattr(resource, name))
        }

    resource_names = [
        name for name in vars(kassa) if not name.startswith("_")
    ]

    for name in resource_names:
        sync_methods = public_names(getattr(kassa, name))
        async_methods = public_names(getattr(async_kassa, name))
        assert sync_methods == async_methods, f"расхождение в ресурсе {name}"
