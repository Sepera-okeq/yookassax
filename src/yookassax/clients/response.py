"""Чтение тела HTTP-ответа."""

from __future__ import annotations

from typing import Any

import httpx

__all__ = ["read_json"]


def read_json(response: httpx.Response) -> Any:
    """Тело ответа как JSON.

    Пустое или неразбираемое тело даёт пустой словарь. Так нужно: например,
    DELETE /webhooks/{id} отвечает вообще без тела, и падать на этом нельзя.
    """
    if not response.content:
        return {}
    try:
        return response.json()
    except ValueError:
        return {}
