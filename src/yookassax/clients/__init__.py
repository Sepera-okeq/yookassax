"""Клиенты в двух режимах.

Оба собраны из общей базы: правила сборки запроса, разбора ответа и повторов
одни и те же. Различается только транспорт.
"""

from .asynchronous import AsyncYooKassa
from .base import BaseClient
from .sync import YooKassa

__all__ = ["AsyncYooKassa", "BaseClient", "YooKassa"]
