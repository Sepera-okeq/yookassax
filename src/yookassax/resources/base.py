"""Общая часть ресурсов и перелистывание списков."""

from __future__ import annotations

from collections.abc import AsyncIterator, Callable, Iterator
from typing import Any

from ..models import Page

__all__ = ["AsyncResource", "Resource", "iterate_pages", "iterate_pages_async"]


class Resource:
    """Синхронный ресурс: знает только своего клиента."""

    def __init__(self, client: Any) -> None:
        self._client = client


class AsyncResource:
    """Асинхронный ресурс."""

    def __init__(self, client: Any) -> None:
        self._client = client


def iterate_pages(
    client: Any,
    build_operation: Callable[..., Any],
    filters: dict[str, Any],
) -> Iterator[Any]:
    """Пройти список до конца, подставляя курсор предыдущей страницы.

    Избавляет вызывающий код от ручной работы с next_cursor.
    """
    cursor: str | None = None
    while True:
        page: Page = client.send(build_operation(**filters, cursor=cursor))
        yield from page
        if not page.has_more:
            return
        cursor = page.next_cursor


async def iterate_pages_async(
    client: Any,
    build_operation: Callable[..., Any],
    filters: dict[str, Any],
) -> AsyncIterator[Any]:
    """Асинхронный вариант iterate_pages."""
    cursor: str | None = None
    while True:
        page: Page = await client.send(build_operation(**filters, cursor=cursor))
        for item in page:
            yield item
        if not page.has_more:
            return
        cursor = page.next_cursor
