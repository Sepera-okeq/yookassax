"""Страница списка."""

from __future__ import annotations

from collections.abc import Iterator, Mapping
from dataclasses import dataclass, field
from typing import Any

from .base import Model, ModelClass

__all__ = ["Page"]


@dataclass(slots=True)
class Page(Model):
    """Страница списка: элементы плюс курсор на следующую.

    По странице можно итерироваться напрямую:

        page = kassa.payments.list(limit=20)
        for payment in page:
            print(payment.id)

    Чтобы пройти всё без ручного перелистывания, у ресурсов есть iterate.
    """

    type: str | None = None
    items: list[Any] = field(default_factory=list)
    next_cursor: str | None = None

    def __iter__(self) -> Iterator[Any]:
        return iter(self.items)

    def __len__(self) -> int:
        return len(self.items)

    def __bool__(self) -> bool:
        return bool(self.items)

    @property
    def has_more(self) -> bool:
        """Есть ли следующая страница.

        Если да, передайте next_cursor в следующий вызов параметром cursor.
        """
        return self.next_cursor is not None

    @classmethod
    def of(
        cls,
        item_model: ModelClass,
        payload: Mapping[str, Any] | None,
    ) -> Page:
        """Собрать страницу, разобрав элементы указанной моделью."""
        data = dict(payload or {})
        raw_items = data.get("items") or []
        return cls(
            raw=data,
            type=data.get("type"),
            items=[item_model.from_api(item) for item in raw_items],
            next_cursor=data.get("next_cursor"),
        )
