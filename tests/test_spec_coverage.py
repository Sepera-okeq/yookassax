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


# Схема спецификации и модель, которой она соответствует. Одна модель может
# закрывать несколько схем: у ЮKassa совпадающие по форме объекты названы
# по-разному в каждом ресурсе.
SCHEMA_TO_MODEL = {
    "MonetaryAmount": "Amount",
    "SbpParticipantBank": "SbpBank",
    "PaymentList": "Page",
    "RefundList": "Page",
    "PayoutsList": "Page",
    "WebhookList": "Page",
    "PaymentCancellationDetails": "CancellationDetails",
    "RefundCancellationDetails": "CancellationDetails",
    "PayoutCancellationDetails": "CancellationDetails",
    "InvoiceCancellationDetails": "CancellationDetails",
    "PersonalDataCancellationDetails": "CancellationDetails",
    "ConfirmationRedirect": "Confirmation",
    "ConfirmationEmbedded": "Confirmation",
    "ConfirmationExternal": "Confirmation",
    "ConfirmationQr": "Confirmation",
    "ConfirmationMobileApplication": "Confirmation",
    "PaymentMethodsConfirmation": "PaymentMethodConfirmation",
    "PaymentMethodsConfirmationQr": "PaymentMethodConfirmation",
    "PaymentMethodsConfirmationRedirect": "PaymentMethodConfirmation",
    "SafeDeal": "Deal",
    "BaseDeal": "Deal",
    "BankCardData": "BankCardData",
    "InvoicingBankCardData": "BankCardData",
    "B2bSberbankPayerBankDetails": "PayerBankDetails",
    "SbpPayerBankDetails": "PayerBankDetails",
    "SavePaymentMethodSbpPayerBankDetails": "PayerBankDetails",
    "B2bSberbankVatData": "B2bSberbankVatData",
    "B2bSberbankCalculatedVatData": "B2bSberbankVatData",
    "B2bSberbankMixedVatData": "B2bSberbankVatData",
    "B2bSberbankUntaxedVatData": "B2bSberbankVatData",
    "Settlement": "Settlement",
    "SettlementPaymentItem": "Settlement",
    "SettlementRefundItem": "Settlement",
    "SettlementPayoutPayment": "Settlement",
    "SettlementPayoutRefund": "Settlement",
    "PayoutDestination": "PayoutDestination",
    "PayoutToCardDestination": "PayoutDestination",
    "PayoutToSbpDestination": "PayoutDestination",
    "PayoutToYooMoneyDestination": "PayoutDestination",
    "RefundMethod": "RefundMethod",
    "SbpRefundMethod": "RefundMethod",
    "ElectronicCertificateRefundMethod": "RefundMethod",
    "ElectronicCertificateRefundDataResponse": "ElectronicCertificateRefundData",
    "RefundSourcesData": "RefundSource",
    "SavePaymentMethod": "PaymentMethod",
    "SavePaymentMethodBankCard": "PaymentMethodBankCard",
    "SavePaymentMethodSbp": "PaymentMethodSbp",
    "DeliveryMethod": "DeliveryMethod",
    "DeliveryMethodEmail": "DeliveryMethod",
    "DeliveryMethodSelf": "DeliveryMethod",
    "DeliveryMethodSms": "DeliveryMethod",
    "PaymentDetails": "InvoicePaymentDetails",
    "PosLinkInfo": "PosLink",
    "PosLinkLastPayment": "PosLinkPayment",
    "ReceiptItemSupplier": "ReceiptItemSupplier",
    "ReceiptItemSupplierWithInn": "ReceiptItemSupplier",
    "ReceiptItemPlannedStatus": None,
    "Metadata": None,
    "Cart": None,
}


def _spec():
    yaml = pytest.importorskip("yaml", reason="для теста нужен pyyaml")
    return yaml.safe_load(SPEC_PATH.read_text(encoding="utf-8"))


def _refs(node, found):
    if isinstance(node, dict):
        if "$ref" in node:
            found.add(node["$ref"].rsplit("/", 1)[-1])
        for value in node.values():
            _refs(value, found)
    elif isinstance(node, list):
        for value in node:
            _refs(value, found)


def _response_schemas(spec):
    """Схемы, которые действительно приходят в ответах, вместе с вложенными."""
    schemas = spec["components"]["schemas"]
    queue: list[str] = []
    for operations_by_method in spec["paths"].values():
        for operation in operations_by_method.values():
            if not isinstance(operation, dict):
                continue
            for code, response in (operation.get("responses") or {}).items():
                if str(code).startswith("2"):
                    found: set[str] = set()
                    _refs(response, found)
                    queue.extend(found)

    closure: set[str] = set()
    while queue:
        name = queue.pop()
        if name in closure or name not in schemas:
            continue
        closure.add(name)
        nested: set[str] = set()
        _refs(schemas[name], nested)
        queue.extend(nested)
    return closure


def _properties(schemas, name, seen=None):
    """Свойства схемы с раскрытием allOf, oneOf и anyOf."""
    seen = seen or set()
    if name in seen or name not in schemas:
        return {}
    seen.add(name)
    node = schemas[name]
    out = dict(node.get("properties", {}))
    for part in node.get("allOf", []) + node.get("oneOf", []) + node.get("anyOf", []):
        out.update(part.get("properties", {}))
        ref = part.get("$ref", "").rsplit("/", 1)[-1]
        if ref:
            out.update(_properties(schemas, ref, seen))
    return out


def _is_object(schemas, name):
    node = schemas[name]
    scalar = node.get("enum") or node.get("type") in (
        "string",
        "integer",
        "boolean",
        "number",
        "array",
    )
    return not scalar and bool(_properties(schemas, name))


@pytest.mark.skipif(not SPEC_PATH.exists(), reason="спецификация не приложена")
def test_every_response_object_has_a_model():
    """У каждого объекта из ответа должна быть модель.

    Иначе поле приезжает словарём, а типов у него нет ни в редакторе, ни в
    mypy. Новый объект в спецификации завалит этот тест, пока его не опишут
    моделью или явно не запишут в SCHEMA_TO_MODEL как ненужный (None).
    """
    spec = _spec()
    schemas = spec["components"]["schemas"]
    ours = {
        name
        for name in models.__all__
        if dataclasses.is_dataclass(getattr(models, name, None))
    }

    unmapped = []
    for name in sorted(_response_schemas(spec)):
        if not _is_object(schemas, name):
            continue
        if name in ours:
            continue
        if name in SCHEMA_TO_MODEL:
            target = SCHEMA_TO_MODEL[name]
            if target is None or target in ours:
                continue
            unmapped.append(f"{name} -> {target} (такой модели нет)")
        else:
            unmapped.append(name)

    assert not unmapped, "объекты ответа без модели: " + ", ".join(unmapped)


@pytest.mark.skipif(not SPEC_PATH.exists(), reason="спецификация не приложена")
def test_models_cover_documented_fields():
    """Поле из спецификации обязано быть в модели.

    Иначе разбор ответа выдаёт UnknownFieldWarning на поле, которое ЮKassa
    документирует давно, и предупреждение перестаёт что-либо значить: его
    начинают глушить фильтром вместе с настоящими новыми полями.
    """
    spec = _spec()
    schemas = spec["components"]["schemas"]

    gaps = []
    for name in sorted(_response_schemas(spec)):
        if not _is_object(schemas, name):
            continue
        model_name = name if hasattr(models, name) else SCHEMA_TO_MODEL.get(name)
        model = getattr(models, model_name, None) if model_name else None
        if model is None or not dataclasses.is_dataclass(model):
            continue

        known = {f.name for f in dataclasses.fields(model)} - {"raw"}
        for missing in sorted(set(_properties(schemas, name)) - known):
            gaps.append(f"{name}.{missing} (модель {model.__name__})")

    assert not gaps, "поля из спецификации не описаны моделями: " + ", ".join(gaps)
