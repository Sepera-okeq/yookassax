"""Общие фикстуры тестов."""

from __future__ import annotations

import pytest

from yookassax import AsyncYooKassa, YooKassa
from yookassax.retry import RetryPolicy
from yookassax.unknown_fields import forget_unknown_fields

API_BASE_URL = "https://api.yookassa.ru/v3"

# Пауза между повторами в тестах не нужна: она только замедляет прогон.
FAST_RETRY = RetryPolicy(attempts=3, backoff=0.001, max_backoff=0.001)


@pytest.fixture(autouse=True)
def forget_reported_fields():
    """Забыть предупреждения предыдущего теста.

    О каждом неизвестном поле говорится один раз за процесс, поэтому без
    сброса тест, идущий вторым, предупреждения уже не увидит.
    """
    forget_unknown_fields()
    yield
    forget_unknown_fields()


@pytest.fixture
def kassa():
    """Синхронный клиент с быстрыми повторами."""
    client = YooKassa(shop_id="123456", secret_key="test_secret")
    client._retry = FAST_RETRY
    with client:
        yield client


@pytest.fixture
async def async_kassa():
    """Асинхронный клиент с быстрыми повторами."""
    client = AsyncYooKassa(shop_id="123456", secret_key="test_secret")
    client._retry = FAST_RETRY
    async with client:
        yield client


@pytest.fixture
def payment_payload() -> dict:
    """Тело ответа с платежом.

    Намеренно содержит поле, которого нет в модели: разбор обязан его
    пережить и сохранить.
    """
    return {
        "id": "22e12f66-000f-5000-8000-18db351245c7",
        "status": "pending",
        "paid": False,
        "amount": {"value": "100.00", "currency": "RUB"},
        "confirmation": {
            "type": "redirect",
            "confirmation_url": "https://yoomoney.ru/checkout/123",
        },
        "created_at": "2026-08-30T10:00:00.000Z",
        "metadata": {"order_id": "42"},
        "field_from_the_future": "значение",
    }
