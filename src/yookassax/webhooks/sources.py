"""Проверка источника уведомления.

Тело уведомления ЮKassa не подписывает, поэтому единственная встроенная
проверка это адрес отправителя. Она отсекает случайные и грубые подделки, но
не заменяет запрос состояния через API.
"""

from __future__ import annotations

import ipaddress

__all__ = ["YOOKASSA_NETWORKS", "is_trusted_ip"]

# Сети, с которых ЮKassa отправляет уведомления.
# Источник: https://yookassa.ru/developers/using-api/webhooks
YOOKASSA_NETWORKS: tuple[str, ...] = (
    "185.71.76.0/27",
    "185.71.77.0/27",
    "77.75.153.0/25",
    "77.75.156.11/32",
    "77.75.156.35/32",
    "77.75.154.128/25",
    "2a02:5180::/32",
)

_TRUSTED_NETWORKS = tuple(
    ipaddress.ip_network(network) for network in YOOKASSA_NETWORKS
)


def is_trusted_ip(ip: str) -> bool:
    """Пришло ли уведомление с адресов ЮKassa.

    Передавайте достоверный адрес отправителя. За обратным прокси это тот,
    который прокси проставляет сам, обычно X-Real-IP из nginx. Левый элемент
    X-Forwarded-For брать нельзя: его подставляет клиент, и проверка теряет
    смысл.

    Неразбираемый адрес считается недоверенным.
    """
    try:
        address = ipaddress.ip_address(ip.strip())
    except ValueError:
        return False

    return any(address in network for network in _TRUSTED_NETWORKS)
