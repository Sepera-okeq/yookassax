"""Прогон по живому API ЮKassa.

Тесты идут в сеть и работают только с ключами тестового магазина. Без ключей
в окружении весь каталог пропускается, поэтому обычный прогон их не замечает.

    export YOOKASSA_SHOP_ID=...
    export YOOKASSA_SECRET_KEY=test_...
    pytest tests/integration

Боевой ключ тест не примет: он создаёт платежи, и на боевом магазине это
настоящие деньги.
"""

from __future__ import annotations

import os

import pytest

from yookassax import AsyncYooKassa, YooKassa

SHOP_ID = os.getenv("YOOKASSA_SHOP_ID")
SECRET_KEY = os.getenv("YOOKASSA_SECRET_KEY")

pytestmark = pytest.mark.skipif(
    not (SHOP_ID and SECRET_KEY),
    reason="нет YOOKASSA_SHOP_ID и YOOKASSA_SECRET_KEY",
)


def pytest_collection_modifyitems(config, items):
    """Пропустить каталог целиком, если ключей нет."""
    if SHOP_ID and SECRET_KEY:
        return
    skip = pytest.mark.skip(reason="нет ключей тестового магазина")
    for item in items:
        if "integration" in str(item.fspath):
            item.add_marker(skip)


def _require_test_key() -> None:
    if SECRET_KEY and not SECRET_KEY.startswith("test_"):
        pytest.fail(
            "YOOKASSA_SECRET_KEY не от тестового магазина: тесты создают платежи"
        )


@pytest.fixture(scope="session")
def live_kassa():
    """Синхронный клиент тестового магазина."""
    _require_test_key()
    with YooKassa(shop_id=SHOP_ID, secret_key=SECRET_KEY) as client:
        yield client


@pytest.fixture
async def live_async_kassa():
    """Асинхронный клиент тестового магазина."""
    _require_test_key()
    async with AsyncYooKassa(shop_id=SHOP_ID, secret_key=SECRET_KEY) as client:
        yield client


@pytest.fixture
def payment_params():
    """Тело платежа, безопасное для тестового магазина."""
    return {
        "amount": {"value": "10.00", "currency": "RUB"},
        "confirmation": {
            "type": "redirect",
            "return_url": "https://example.com/done",
        },
        "capture": True,
        "description": "Проверка yookassax",
        "metadata": {"source": "yookassax-tests"},
    }
