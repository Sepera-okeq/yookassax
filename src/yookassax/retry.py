"""Политика повторов.

Повторяем то, что почти наверняка пройдёт со второй попытки, и не повторяем
ошибки данных: на неверный параметр API ответит так же и во второй раз.
"""

from __future__ import annotations

import random
from dataclasses import dataclass

from .errors import RateLimited, ResponseProcessing, ServerError

__all__ = ["RetryPolicy", "should_retry"]


@dataclass(frozen=True, slots=True)
class RetryPolicy:
    """Сколько раз повторять и с какими паузами.

    Поле attempts считает ВСЕ попытки, включая первую: значение 1 означает
    "не повторять вовсе".

    Пауза растёт экспоненциально и слегка дрожит. Дрожание нужно, чтобы пачка
    клиентов, одновременно получившая 429, не пошла на второй круг тоже
    одновременно и не получила его снова.
    """

    attempts: int = 3
    backoff: float = 0.5
    max_backoff: float = 8.0

    def delay(self, attempt: int) -> float:
        """Пауза перед попыткой с номером attempt (нумерация с единицы)."""
        base = min(self.backoff * (2 ** (attempt - 1)), self.max_backoff)
        jitter = 0.5 + random.random() / 2
        return base * jitter


def should_retry(error: Exception) -> bool:
    """Стоит ли повторять запрос после этой ошибки.

    Повторяем:
      202 - ЮKassa приняла запрос и ещё считает;
      429 - превышена частота запросов;
      500 - сбой на стороне ЮKassa.

    Не повторяем 400 и 404: это ошибки самого запроса.

    Сетевые обрывы обрабатываются отдельно в клиенте. Там важно, что повтор
    идёт с тем же ключом идемпотентности, иначе можно создать второй платёж.
    """
    return isinstance(error, (ResponseProcessing, RateLimited, ServerError))
