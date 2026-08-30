"""Базовый класс моделей и разбор примитивов.

Два решения, которые стоит понимать сразу.

Обычные dataclass-ы, без pydantic. Библиотека тянет одну зависимость (httpx) и
не навязывает приложению версию валидатора. Типов хватает и для подсказок в
редакторе, и для чтения кода.

Неизвестные поля не роняют разбор. ЮKassa добавляет поля в ответы, и строгая
модель превратила бы это в отказ обслуживать платежи. Всё, чего нет в модели,
остаётся в словаре raw, а метод extra даёт к нему доступ.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field, fields
from datetime import datetime
from decimal import Decimal, InvalidOperation
from typing import Any, ClassVar, TypeVar

__all__ = ["Model", "ModelClass", "parse_datetime", "parse_decimal"]

ModelType = TypeVar("ModelType", bound="Model")

# Псевдоним нужен из-за поля type у части моделей: оно перекрывает
# встроенный type, и аннотация dict[str, type] начинает ссылаться на поле,
# а не на класс. Псевдоним объявлен здесь, где перекрытия нет.
ModelClass = type["Model"]


def parse_datetime(value: Any) -> datetime | None:
    """Строка ISO 8601 из API в datetime.

    API отдаёт время с суффиксом Z. До Python 3.11 fromisoformat такой формат
    не понимает, поэтому заменяем Z на явное смещение.
    """
    if not value:
        return None
    if isinstance(value, datetime):
        return value

    text = str(value)
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"

    try:
        return datetime.fromisoformat(text)
    except ValueError:
        return None


def parse_decimal(value: Any) -> Decimal | None:
    """Сумма из API в Decimal.

    Суммы приходят строками ("100.00"), так их и разбираем. Через str, а не
    Decimal(float): Decimal(0.1) даёт 0.1000000000000000055, и на деньгах это
    уже расхождение.
    """
    if value is None:
        return None
    if isinstance(value, Decimal):
        return value

    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError):
        return None


@dataclass(slots=True)
class Model:
    """Общий разбор ответа: известные поля по типам, остальное в raw."""

    raw: dict[str, Any] = field(default_factory=dict, repr=False, compare=False)

    # Поля, требующие преобразования. Заполняются в наследниках.
    datetime_fields: ClassVar[tuple[str, ...]] = ()
    decimal_fields: ClassVar[tuple[str, ...]] = ()
    nested_models: ClassVar[dict[str, ModelClass]] = {}
    nested_lists: ClassVar[dict[str, ModelClass]] = {}

    @classmethod
    def from_api(
        cls: type[ModelType],
        payload: Mapping[str, Any] | None,
    ) -> ModelType:
        """Собрать модель из тела ответа API."""
        data = dict(payload or {})
        known_names = {f.name for f in fields(cls)} - {"raw"}
        kwargs: dict[str, Any] = {}

        for name in known_names:
            if name not in data:
                continue

            value = data[name]
            if name in cls.datetime_fields:
                value = parse_datetime(value)
            elif name in cls.decimal_fields:
                value = parse_decimal(value)
            elif name in cls.nested_models and isinstance(value, Mapping):
                value = cls.nested_models[name].from_api(value)
            elif name in cls.nested_lists and isinstance(value, list):
                item_model = cls.nested_lists[name]
                value = [item_model.from_api(item) for item in value]

            kwargs[name] = value

        return cls(raw=data, **kwargs)

    def extra(self, key: str, default: Any = None) -> Any:
        """Поле, которого ещё нет в модели.

        Нужно, когда API начал отдавать что-то новое, а библиотека ещё не
        обновилась.
        """
        return self.raw.get(key, default)
