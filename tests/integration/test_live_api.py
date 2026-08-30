"""Проверки по живому API тестового магазина."""

from __future__ import annotations

import dataclasses
import uuid
import warnings
from decimal import Decimal

import pytest

from yookassax import BadRequest, NotFound, UnknownFieldWarning
from yookassax.models import Model, PaymentMethod


def test_settings_are_readable(live_kassa):
    """GET /me отвечает и разбирается. Заодно проверка, что ключи рабочие."""
    me = live_kassa.settings.get()

    assert me.account_id
    assert me.status == "enabled"
    assert me.test is True, "ключи должны быть от тестового магазина"


def test_payment_is_created_and_parsed(live_kassa, payment_params):
    payment = live_kassa.payments.create(payment_params)

    assert payment.id
    assert payment.is_pending
    assert payment.amount.value == Decimal("10.00")
    assert payment.amount.currency == "RUB"
    # Время всегда с зоной: наивная дата ломает арифметику на стороне магазина.
    assert payment.created_at.tzinfo is not None
    assert payment.confirmation_url.startswith("https://")
    assert payment.metadata == {"source": "yookassax-tests"}
    assert payment.test is True


def test_idempotency_key_prevents_a_second_payment(live_kassa, payment_params):
    """Повтор с тем же ключом обязан вернуть тот же платёж, а не создать новый."""
    key = f"yookassax-test-{uuid.uuid4()}"

    first = live_kassa.payments.create(payment_params, idempotency_key=key)
    second = live_kassa.payments.create(payment_params, idempotency_key=key)

    assert first.id == second.id


def test_payment_is_fetched_by_id(live_kassa, payment_params):
    created = live_kassa.payments.create(payment_params)

    fetched = live_kassa.payments.get(created.id)

    assert fetched.id == created.id
    assert fetched.amount.value == created.amount.value


def test_list_and_iterate_agree(live_kassa):
    page = live_kassa.payments.list(limit=5)

    assert len(page) <= 5
    if page.has_more:
        assert page.next_cursor

    walked = []
    for payment in live_kassa.payments.iterate(limit=3):
        walked.append(payment.id)
        if len(walked) >= 7:
            break

    assert len(walked) == len(set(walked)), "iterate не должен повторять объекты"


def test_bad_request_carries_the_details(live_kassa):
    """Ошибка данных разобрана в поля, а не в текст."""
    with pytest.raises(BadRequest) as error:
        live_kassa.payments.create({"amount": {"value": "0.00", "currency": "RUB"}})

    assert error.value.status == 400
    assert error.value.code
    assert error.value.description
    assert error.value.request_id


def test_missing_payment_raises_not_found(live_kassa):
    with pytest.raises(NotFound):
        live_kassa.payments.get("00000000-0000-0000-0000-000000000000")


def test_saved_payment_method_is_typed(live_kassa):
    """Привязка способа оплаты разбирается в модель своего типа."""
    method = live_kassa.payment_methods.create(
        {
            "type": "bank_card",
            "confirmation": {
                "type": "redirect",
                "return_url": "https://example.com/saved",
            },
        }
    )

    assert isinstance(method, PaymentMethod)
    assert method.type == "bank_card"
    assert method.confirmation.confirmation_url.startswith("https://")


async def test_async_client_reads_the_same_shop(live_async_kassa, payment_params):
    """Асинхронный режим ходит в то же API и разбирает так же."""
    me = await live_async_kassa.settings.get()
    payment = await live_async_kassa.payments.create(payment_params)

    assert me.test is True
    assert payment.is_pending
    assert payment.amount.value == Decimal("10.00")

    async for item in live_async_kassa.payments.iterate(limit=2):
        assert item.id
        break


def _unknown_fields(obj, found):
    """Поля живого ответа, которых нет в модели."""
    if isinstance(obj, Model):
        known = {f.name for f in dataclasses.fields(obj)} - {"raw"}
        for name in set(obj.raw) - known:
            found.setdefault(type(obj).__name__, set()).add(name)
        for field in dataclasses.fields(obj):
            if field.name != "raw":
                _unknown_fields(getattr(obj, field.name), found)
    elif isinstance(obj, list):
        for item in obj:
            _unknown_fields(item, found)


def test_real_responses_have_no_unknown_fields(live_kassa):
    """Главная проверка: модели описывают реальные ответы целиком.

    Спецификация отстаёт от API - так нашлись protocol, method_completed и
    challenge_completed у 3-D Secure. Здесь смотрим не на спецификацию, а на
    то, что магазин отдаёт на самом деле.
    """
    found: dict[str, set[str]] = {}

    with warnings.catch_warnings():
        warnings.simplefilter("ignore", UnknownFieldWarning)
        _unknown_fields(live_kassa.settings.get(), found)
        for number, payment in enumerate(live_kassa.payments.iterate(limit=50), 1):
            _unknown_fields(payment, found)
            if number >= 50:
                break
        for refund in live_kassa.refunds.iterate(limit=20):
            _unknown_fields(refund, found)

    assert not found, "в живых ответах есть поля без моделей: " + ", ".join(
        f"{model}: {sorted(fields)}" for model, fields in sorted(found.items())
    )
