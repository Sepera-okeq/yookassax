"""Платёж: центральный объект API."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime
from typing import Any, ClassVar

from .base import Model, ModelClass
from .common import (
    Amount,
    AuthorizationDetails,
    BankCardData,
    CancellationDetails,
    Confirmation,
    PayerBankDetails,
    Recipient,
    Settlement,
    Transfer,
)

__all__ = [
    "PAYMENT_METHOD_MODELS",
    "B2bSberbankVatData",
    "ElectronicCertificate",
    "ElectronicCertificateApprovedPaymentArticle",
    "ElectronicCertificatePayment",
    "InvoiceDetails",
    "PaymentDealInfo",
    "PaymentMethodConfirmation",
    "Payment",
    "PaymentMethod",
    "PaymentMethodAlfaPay",
    "PaymentMethodAlfabank",
    "PaymentMethodApplePay",
    "PaymentMethodB2bSberbank",
    "PaymentMethodBankCard",
    "PaymentMethodCash",
    "PaymentMethodElectronicCertificate",
    "PaymentMethodGooglePay",
    "PaymentMethodInstallments",
    "PaymentMethodMobileBalance",
    "PaymentMethodQiwi",
    "PaymentMethodSberBnpl",
    "PaymentMethodSberLoan",
    "PaymentMethodSberbank",
    "PaymentMethodSbp",
    "PaymentMethodTinkoffBank",
    "PaymentMethodWeChat",
    "PaymentMethodWebmoney",
    "PaymentMethodYooMoney",
]


@dataclass(slots=True)
class ElectronicCertificate(Model):
    """Электронный сертификат, которым оплачена позиция."""

    certificate_id: str | None = None
    tru_quantity: int | None = None
    applied_compensation: Amount | None = None
    available_compensation: Amount | None = None

    nested_models: ClassVar[dict[str, ModelClass]] = {
        "applied_compensation": Amount,
        "available_compensation": Amount,
    }


@dataclass(slots=True)
class ElectronicCertificatePayment(Model):
    """Данные ФЭС НСПК по оплате сертификатом."""

    amount: Amount | None = None
    basket_id: str | None = None

    nested_models: ClassVar[dict[str, ModelClass]] = {"amount": Amount}


@dataclass(slots=True)
class ElectronicCertificateApprovedPaymentArticle(Model):
    """Позиция корзины, одобренной к оплате сертификатом."""

    article_number: int | None = None
    article_code: str | None = None
    tru_code: str | None = None
    certificates: list[ElectronicCertificate] | None = None

    nested_lists: ClassVar[dict[str, ModelClass]] = {
        "certificates": ElectronicCertificate,
    }


@dataclass(slots=True)
class B2bSberbankVatData(Model):
    """НДС при оплате по счёту от юридического лица.

    Значение type: calculated - налог посчитан, untaxed - не облагается,
    mixed - в счёте разные ставки.
    """

    type: str | None = None
    rate: str | None = None
    amount: Amount | None = None

    nested_models: ClassVar[dict[str, ModelClass]] = {"amount": Amount}


@dataclass(slots=True)
class PaymentDealInfo(Model):
    """Сделка, в составе которой идёт платёж."""

    id: str | None = None
    settlements: list[Settlement] | None = None

    nested_lists: ClassVar[dict[str, ModelClass]] = {"settlements": Settlement}


@dataclass(slots=True)
class PaymentMethodConfirmation(Model):
    """Подтверждение привязки способа оплаты."""

    type: str | None = None
    confirmation_url: str | None = None
    confirmation_data: str | None = None
    return_url: str | None = None
    enforce: bool | None = None


@dataclass(slots=True)
class PaymentMethod(Model):
    """Способ оплаты.

    Если saved равно True, по этому способу можно списывать повторно, передав
    его идентификатор в payment_method_id при создании нового платежа.
    """

    id: str | None = None
    type: str | None = None
    saved: bool | None = None
    status: str | None = None
    title: str | None = None
    card: BankCardData | None = None
    account_number: str | None = None
    login: str | None = None
    phone: str | None = None
    payer_bank_details: PayerBankDetails | None = None
    sbp_operation_id: str | None = None
    # Приходят только из /payment_methods, при привязке способа оплаты.
    confirmation: PaymentMethodConfirmation | None = None
    holder: dict[str, Any] | None = None
    metadata: dict[str, Any] | None = None

    nested_models: ClassVar[dict[str, ModelClass]] = {
        "card": BankCardData,
        "payer_bank_details": PayerBankDetails,
        "confirmation": PaymentMethodConfirmation,
    }

    @classmethod
    def from_api(cls, payload: Mapping[str, Any] | None) -> PaymentMethod:
        """Собрать модель, подходящую под значение type.

        Возвращает подходящий подкласс, поэтому у оплаты по сертификату сразу
        есть articles, а у кредита Сбербанка loan_option. Для типа, которого
        библиотека ещё не знает, остаётся сам PaymentMethod: неизвестный способ
        оплаты не должен ронять разбор платежа.
        """
        if cls is PaymentMethod and payload is not None:
            model = PAYMENT_METHOD_MODELS.get(str(payload.get("type") or ""))
            if model is not None:
                return model.from_api(payload)
        # super() без аргументов здесь не работает: dataclass(slots=True)
        # пересоздаёт класс, и ссылка на исходный остаётся протухшей.
        return super(PaymentMethod, cls).from_api(payload)


@dataclass(slots=True)
class PaymentMethodBankCard(PaymentMethod):
    """Банковская карта."""


@dataclass(slots=True)
class PaymentMethodYooMoney(PaymentMethod):
    """Кошелёк ЮMoney."""


@dataclass(slots=True)
class PaymentMethodSberbank(PaymentMethod):
    """СберБанк Онлайн."""


@dataclass(slots=True)
class PaymentMethodTinkoffBank(PaymentMethod):
    """Т-Банк."""


@dataclass(slots=True)
class PaymentMethodAlfabank(PaymentMethod):
    """Альфа-Клик."""


@dataclass(slots=True)
class PaymentMethodAlfaPay(PaymentMethod):
    """Alfa Pay."""


@dataclass(slots=True)
class PaymentMethodSbp(PaymentMethod):
    """Система быстрых платежей."""


@dataclass(slots=True)
class PaymentMethodCash(PaymentMethod):
    """Наличные."""


@dataclass(slots=True)
class PaymentMethodMobileBalance(PaymentMethod):
    """Баланс телефона."""


@dataclass(slots=True)
class PaymentMethodQiwi(PaymentMethod):
    """QIWI Кошелёк."""


@dataclass(slots=True)
class PaymentMethodWebmoney(PaymentMethod):
    """WebMoney."""


@dataclass(slots=True)
class PaymentMethodWeChat(PaymentMethod):
    """WeChat Pay."""


@dataclass(slots=True)
class PaymentMethodApplePay(PaymentMethod):
    """Apple Pay."""


@dataclass(slots=True)
class PaymentMethodGooglePay(PaymentMethod):
    """Google Pay."""


@dataclass(slots=True)
class PaymentMethodInstallments(PaymentMethod):
    """Заплатить по частям."""


@dataclass(slots=True)
class PaymentMethodSberBnpl(PaymentMethod):
    """Оплата частями от СберБанка."""


@dataclass(slots=True)
class PaymentMethodB2bSberbank(PaymentMethod):
    """Сбербанк Бизнес Онлайн: оплата по счёту от юридического лица."""

    payment_purpose: str | None = None
    vat_data: B2bSberbankVatData | None = None

    nested_models: ClassVar[dict[str, ModelClass]] = {
        "card": BankCardData,
        "payer_bank_details": PayerBankDetails,
        "confirmation": PaymentMethodConfirmation,
        "vat_data": B2bSberbankVatData,
    }


@dataclass(slots=True)
class PaymentMethodSberLoan(PaymentMethod):
    """Кредит или рассрочка от СберБанка."""

    loan_option: str | None = None
    discount_amount: Amount | None = None
    # Конец периода охлаждения: до него деньги магазину не переводятся.
    suspended_until: datetime | None = None

    datetime_fields: ClassVar[tuple[str, ...]] = ("suspended_until",)
    nested_models: ClassVar[dict[str, ModelClass]] = {
        "card": BankCardData,
        "payer_bank_details": PayerBankDetails,
        "confirmation": PaymentMethodConfirmation,
        "discount_amount": Amount,
    }


@dataclass(slots=True)
class PaymentMethodElectronicCertificate(PaymentMethod):
    """Электронный сертификат: карта «Мир» с сертификатом ФСС."""

    electronic_certificate: ElectronicCertificatePayment | None = None
    # Корзина, одобренная к оплате сертификатом. Приходит только с готовой
    # страницы ЮKassa, при своей форме оплаты её не будет.
    articles: list[ElectronicCertificateApprovedPaymentArticle] | None = None

    nested_models: ClassVar[dict[str, ModelClass]] = {
        "card": BankCardData,
        "payer_bank_details": PayerBankDetails,
        "confirmation": PaymentMethodConfirmation,
        "electronic_certificate": ElectronicCertificatePayment,
    }
    nested_lists: ClassVar[dict[str, ModelClass]] = {
        "articles": ElectronicCertificateApprovedPaymentArticle,
    }


# Значение поля type и модель, которой разбирать такой способ оплаты.
PAYMENT_METHOD_MODELS: dict[str, type[PaymentMethod]] = {
    "bank_card": PaymentMethodBankCard,
    "yoo_money": PaymentMethodYooMoney,
    "sberbank": PaymentMethodSberbank,
    "tinkoff_bank": PaymentMethodTinkoffBank,
    "alfabank": PaymentMethodAlfabank,
    "alfa_pay": PaymentMethodAlfaPay,
    "sbp": PaymentMethodSbp,
    "cash": PaymentMethodCash,
    "mobile_balance": PaymentMethodMobileBalance,
    "qiwi": PaymentMethodQiwi,
    "webmoney": PaymentMethodWebmoney,
    "wechat": PaymentMethodWeChat,
    "apple_pay": PaymentMethodApplePay,
    "google_pay": PaymentMethodGooglePay,
    "installments": PaymentMethodInstallments,
    "sber_bnpl": PaymentMethodSberBnpl,
    "b2b_sberbank": PaymentMethodB2bSberbank,
    "sber_loan": PaymentMethodSberLoan,
    "electronic_certificate": PaymentMethodElectronicCertificate,
}


@dataclass(slots=True)
class InvoiceDetails(Model):
    """Ссылка на счёт, по которому прошёл платёж."""

    id: str | None = None


@dataclass(slots=True)
class Payment(Model):
    """Платёж."""

    id: str | None = None
    status: str | None = None
    amount: Amount | None = None
    income_amount: Amount | None = None
    refunded_amount: Amount | None = None
    description: str | None = None
    recipient: Recipient | None = None
    payment_method: PaymentMethod | None = None
    confirmation: Confirmation | None = None
    cancellation_details: CancellationDetails | None = None
    authorization_details: AuthorizationDetails | None = None
    transfers: list[Transfer] | None = None
    # В платеже приходит не сделка целиком, а её идентификатор и расчёты.
    deal: PaymentDealInfo | None = None
    invoice_details: InvoiceDetails | None = None
    created_at: datetime | None = None
    captured_at: datetime | None = None
    expires_at: datetime | None = None
    paid: bool | None = None
    refundable: bool | None = None
    test: bool | None = None
    receipt_registration: str | None = None
    merchant_customer_id: str | None = None
    metadata: dict[str, Any] | None = None

    datetime_fields: ClassVar[tuple[str, ...]] = (
        "created_at",
        "captured_at",
        "expires_at",
    )
    nested_models: ClassVar[dict[str, ModelClass]] = {
        "amount": Amount,
        "income_amount": Amount,
        "refunded_amount": Amount,
        "recipient": Recipient,
        "payment_method": PaymentMethod,
        "confirmation": Confirmation,
        "cancellation_details": CancellationDetails,
        "authorization_details": AuthorizationDetails,
        "deal": PaymentDealInfo,
        "invoice_details": InvoiceDetails,
    }
    nested_lists: ClassVar[dict[str, ModelClass]] = {"transfers": Transfer}

    @property
    def is_succeeded(self) -> bool:
        """Платёж прошёл, деньги у магазина."""
        return self.status == "succeeded"

    @property
    def is_pending(self) -> bool:
        """Платёж создан, плательщик ещё не завершил оплату."""
        return self.status == "pending"

    @property
    def is_waiting_for_capture(self) -> bool:
        """Деньги захолдированы, нужен вызов capture или cancel."""
        return self.status == "waiting_for_capture"

    @property
    def is_canceled(self) -> bool:
        """Платёж отменён, деньги у плательщика."""
        return self.status == "canceled"

    @property
    def confirmation_url(self) -> str | None:
        """Ссылка, куда вести плательщика.

        Возвращает None, если сценарий подтверждения не предполагает редиректа,
        например для виджета или списания по сохранённому способу.
        """
        if self.confirmation is None:
            return None
        return self.confirmation.confirmation_url
