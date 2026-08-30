"""Покрытие официальной спецификации OpenAPI.

Спецификация лежит рядом, в docs/yookassa-openapi.yaml, и служит контрактом:
если ЮKassa добавит эндпоинт, тест покажет, чего библиотеке не хватает. Он же
ловит опечатки в путях, которые иначе всплыли бы только в бою.

Именно так нашлась ошибка в кассовых ссылках: метод SDK называется
change_recipient, а путь в API просто /recipient.
"""

from __future__ import annotations

import dataclasses
import inspect
import re
from pathlib import Path

import pytest

from yookassax import models, operations

SPEC_PATH = Path(__file__).resolve().parents[1] / "docs" / "yookassa-openapi.yaml"

HTTP_METHODS = ("get", "post", "put", "delete", "patch")

# Эндпоинты, которых нет в публичной спецификации, но которые существуют и
# поддержаны официальным SDK. Каждая запись должна объяснять причину.
NOT_IN_SPEC = {
    ("POST", "/self_employed"): "продукт выплат самозанятым, документирован отдельно",
    ("GET", "/self_employed/{id}"): "то же самое",
}


def _placeholder(path: str) -> str:
    """Привести шаблон пути к общему виду: {payment_id} и {id} равнозначны."""
    return re.sub(r"\{[^}]+\}", "{id}", path)


def _spec_routes() -> set[tuple[str, str]]:
    yaml = pytest.importorskip("yaml", reason="для теста нужен pyyaml")
    spec = yaml.safe_load(SPEC_PATH.read_text(encoding="utf-8"))
    return {
        (method.upper(), _placeholder(path))
        for path, operations_by_method in spec["paths"].items()
        for method in operations_by_method
        if method in HTTP_METHODS
    }


def _library_routes() -> dict[tuple[str, str], str]:
    """Маршруты, которые описывает библиотека, и имена их построителей."""
    routes: dict[tuple[str, str], str] = {}

    for module_name in operations.__all__:
        module = getattr(operations, module_name)
        for function_name in getattr(module, "__all__", []):
            function = getattr(module, function_name)
            # Обязательные позиционные аргументы заполняем заглушкой,
            # чтобы получить готовое описание операции.
            stub_args = [
                "X"
                for parameter in inspect.signature(function).parameters.values()
                if parameter.default is inspect.Parameter.empty
                and parameter.kind
                not in (parameter.VAR_KEYWORD, parameter.KEYWORD_ONLY)
            ]
            operation = function(*stub_args)
            path = re.sub(r"/X(?=/|$)", "/{id}", operation.path)
            routes[(operation.method, path)] = f"{module_name}.{function_name}"

    return routes


@pytest.mark.skipif(not SPEC_PATH.exists(), reason="спецификация не приложена")
def test_every_spec_route_is_implemented():
    missing = _spec_routes() - set(_library_routes())

    assert not missing, "не реализованы маршруты: " + ", ".join(
        f"{method} {path}" for method, path in sorted(missing)
    )


@pytest.mark.skipif(not SPEC_PATH.exists(), reason="спецификация не приложена")
def test_library_has_no_unknown_routes():
    """Путь, которого нет в спеке, это либо опечатка, либо осознанное исключение."""
    library = _library_routes()
    unknown = set(library) - _spec_routes() - set(NOT_IN_SPEC)

    assert not unknown, "маршруты вне спецификации: " + ", ".join(
        f"{method} {path} ({library[(method, path)]})"
        for method, path in sorted(unknown)
    )


@pytest.mark.skipif(not SPEC_PATH.exists(), reason="спецификация не приложена")
def test_models_cover_documented_fields():
    """Поле из спецификации обязано быть в модели.

    Иначе разбор ответа выдаст UnknownFieldWarning на поле, которое ЮKassa
    документирует давно, и предупреждение перестанет что-либо значить: его
    начнут глушить фильтром вместе с настоящими новыми полями.
    """
    yaml = pytest.importorskip("yaml", reason="для теста нужен pyyaml")
    schemas = yaml.safe_load(SPEC_PATH.read_text(encoding="utf-8"))["components"][
        "schemas"
    ]

    gaps = []
    for name in models.__all__:
        model = getattr(models, name)
        if not dataclasses.is_dataclass(model) or name not in schemas:
            continue

        known = {f.name for f in dataclasses.fields(model)} - {"raw"}
        for missing in sorted(set(schemas[name].get("properties", {})) - known):
            gaps.append(f"{name}.{missing}")

    assert not gaps, "поля из спецификации не описаны моделями: " + ", ".join(gaps)
