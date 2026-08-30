"""Предупреждение о полях, которых нет в моделях."""

from __future__ import annotations

import warnings

import pytest

from yookassax import Payment, UnknownFieldWarning
from yookassax.models import Page


def test_unknown_field_raises_warning():
    with pytest.warns(UnknownFieldWarning) as caught:
        Payment.from_api({"id": "p1", "surprise": 1})

    assert "surprise" in str(caught[0].message)


def test_warning_names_the_model_and_suggests_an_update():
    """Из текста должно быть понятно, где поле и что с этим делать."""
    with pytest.warns(UnknownFieldWarning) as caught:
        Payment.from_api({"id": "p1", "surprise": 1})

    message = str(caught[0].message)
    assert "Payment" in message
    assert "surprise" in message
    assert "yookassax" in message


def test_known_payload_is_quiet(payment_payload):
    """Штатный ответ предупреждений не даёт."""
    known = {
        key: value
        for key, value in payment_payload.items()
        if key != "field_from_the_future"
    }

    with warnings.catch_warnings():
        warnings.simplefilter("error", UnknownFieldWarning)
        Payment.from_api(known)


def test_repeated_field_warns_once():
    """Страница из ста платежей не должна давать сто одинаковых строк."""
    body = {"id": "p1", "surprise": 1}

    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        for _ in range(100):
            Payment.from_api(body)

    assert len(caught) == 1


def test_new_field_warns_even_after_the_first_one():
    """Второе новое поле не должно потеряться из-за первого."""
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        Payment.from_api({"id": "p1", "surprise": 1})
        Payment.from_api({"id": "p1", "surprise": 1, "another": 2})

    assert len(caught) == 2
    assert "another" in str(caught[1].message)


def test_same_field_in_another_model_warns_again():
    """Поле принадлежит модели: одноимённое в другой модели это другой случай."""
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        Payment.from_api({"surprise": 1})
        Page.of(Payment, {"items": [{"surprise": 1}]})

    assert len(caught) == 1

    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        Payment.from_api({"surprise": 1})

    assert not caught


def test_warning_can_be_silenced():
    """Приложению, которому это не нужно, хватает штатного фильтра."""
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        warnings.filterwarnings("ignore", category=UnknownFieldWarning)
        Payment.from_api({"id": "p1", "surprise": 1})

    assert not caught


def test_value_is_still_available(payment_payload):
    """Предупреждение не отменяет доступ к значению."""
    with pytest.warns(UnknownFieldWarning):
        payment = Payment.from_api(payment_payload)

    assert payment.extra("field_from_the_future") == "значение"


def test_nested_model_warns_about_its_own_fields():
    """Вложенный объект разбирается своей моделью, ей и принадлежит поле."""
    with pytest.warns(UnknownFieldWarning) as caught:
        Payment.from_api(
            {"amount": {"value": "1.00", "currency": "RUB", "surprise": 1}}
        )

    assert "Amount" in str(caught[0].message)


def test_warning_points_at_the_calling_code():
    """Строка в предупреждении должна быть из приложения, а не из библиотеки.

    Уровень стека считается на месте: у модели верхнего уровня и у вложенной
    разная глубина, и фиксированное число ошибается на одну из них.
    """
    with pytest.warns(UnknownFieldWarning) as caught:
        Payment.from_api({"surprise": 1})

    assert caught[0].filename == __file__
