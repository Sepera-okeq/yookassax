"""Учётные данные для доступа к API.

Ключи хранятся в экземпляре клиента, а не в глобальной переменной. Это
осознанное отличие от официального SDK, где Configuration держит их на классе:
при работе с несколькими магазинами из одного процесса два платежа могут
переписать токен друг другу между настройкой и вызовом, и платёж уйдёт через
чужой магазин. Здесь такое невозможно.
"""

from __future__ import annotations

from base64 import b64encode
from dataclasses import dataclass

from .errors import ConfigurationError

__all__ = ["Credentials"]


@dataclass(frozen=True, slots=True)
class Credentials:
    """Пара shop_id + secret_key либо OAuth-токен.

    Первый способ используют для своего магазина, второй - когда приложение
    работает с чужими магазинами по выданному ими доступу.
    """

    shop_id: str | None = None
    secret_key: str | None = None
    oauth_token: str | None = None

    @classmethod
    def build(
        cls,
        shop_id: str | int | None,
        secret_key: str | None,
        oauth_token: str | None,
    ) -> Credentials:
        """Собрать и сразу проверить набор ключей."""
        if oauth_token:
            if shop_id or secret_key:
                raise ConfigurationError(
                    "Заданы одновременно oauth_token и shop_id/secret_key. "
                    "Выберите один способ: OAuth для чужих магазинов, "
                    "пара shop_id и secret_key для своего."
                )
            return cls(oauth_token=oauth_token)

        if not (shop_id and secret_key):
            raise ConfigurationError(
                "Нужны либо shop_id и secret_key, либо oauth_token."
            )
        return cls(shop_id=str(shop_id), secret_key=str(secret_key))

    def authorization_header(self) -> str:
        """Значение заголовка Authorization для запроса."""
        if self.oauth_token:
            return f"Bearer {self.oauth_token}"
        pair = f"{self.shop_id}:{self.secret_key}".encode()
        return f"Basic {b64encode(pair).decode()}"
