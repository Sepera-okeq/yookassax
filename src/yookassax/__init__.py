"""yookassax: неофициальный клиент ЮKassa для Python в двух режимах.

С ЮKassa и ЮMoney проект не связан, ими не поддерживается и их продуктом не
является. Официальный SDK называется yookassa.

Быстрый старт, синхронно:

    from yookassax import YooKassa

    with YooKassa(shop_id="123456", secret_key="live_...") as kassa:
        payment = kassa.payments.create({
            "amount": {"value": "100.00", "currency": "RUB"},
            "confirmation": {
                "type": "redirect",
                "return_url": "https://example.com/done",
            },
            "capture": True,
            "description": "Заказ 42",
        })
        print(payment.confirmation_url)

То же самое асинхронно:

    from yookassax import AsyncYooKassa

    async with AsyncYooKassa(shop_id="123456", secret_key="live_...") as kassa:
        payment = await kassa.payments.create({...})

Чем отличается от официального SDK:

Ключи хранятся в экземпляре клиента, а не на классе. Официальный SDK держит их
в Configuration на уровне класса, поэтому при работе с несколькими магазинами
из одного процесса два платежа могут переписать токен друг другу и платёж
уйдёт через чужой магазин.

Асинхронный режим настоящий. Официальный SDK синхронный, внутри requests, и
вызов из асинхронного обработчика останавливает весь воркер.

Ключ идемпотентности проставляется автоматически на всех изменяющих запросах,
а повторы после обрыва идут с тем же ключом, поэтому второго платежа не
возникает.

Повторы на кодах 202, 429 и 500 с экспоненциальной паузой.

Модели типизированы и терпимы к новым полям API: неизвестное складывается в
raw и доступно через метод extra. О каждом таком поле один раз выдаётся
UnknownFieldWarning: значит, ЮKassa расширила ответ и стоит обновить
библиотеку.
"""

from . import webhooks
from ._version import __version__
from .clients import AsyncYooKassa, YooKassa
from .errors import (
    APIError,
    BadRequest,
    ConfigurationError,
    Forbidden,
    Gone,
    NotFound,
    RateLimited,
    ResponseProcessing,
    ServerError,
    TransportError,
    Unauthorized,
    YooKassaError,
)
from .models import (
    Amount,
    AuthorizationDetails,
    B2bSberbankVatData,
    BankCardData,
    BankCardProduct,
    CancellationDetails,
    Confirmation,
    Deal,
    DeliveryMethod,
    ElectronicCertificate,
    ElectronicCertificateApprovedPaymentArticle,
    ElectronicCertificatePayment,
    ElectronicCertificateRefundArticle,
    ElectronicCertificateRefundData,
    FiscalizationData,
    IncomeReceipt,
    IndustryDetails,
    Invoice,
    InvoiceDetails,
    InvoicePaymentDetails,
    LineItem,
    MarkCodeInfo,
    MarkQuantity,
    Me,
    OperationalDetails,
    Page,
    PayerBankDetails,
    Payment,
    PaymentDealInfo,
    PaymentMethod,
    PaymentMethodAlfabank,
    PaymentMethodAlfaPay,
    PaymentMethodApplePay,
    PaymentMethodB2bSberbank,
    PaymentMethodBankCard,
    PaymentMethodCash,
    PaymentMethodConfirmation,
    PaymentMethodElectronicCertificate,
    PaymentMethodGooglePay,
    PaymentMethodInstallments,
    PaymentMethodMobileBalance,
    PaymentMethodQiwi,
    PaymentMethodSberbank,
    PaymentMethodSberBnpl,
    PaymentMethodSberLoan,
    PaymentMethodSbp,
    PaymentMethodTinkoffBank,
    PaymentMethodWebmoney,
    PaymentMethodWeChat,
    PaymentMethodYooMoney,
    Payout,
    PayoutCardData,
    PayoutDealInfo,
    PayoutDestination,
    PayoutSelfEmployedInfo,
    PersonalData,
    PosLink,
    PosLinkPayment,
    Receipt,
    ReceiptItem,
    ReceiptItemSupplier,
    Recipient,
    Refund,
    RefundAuthorizationDetails,
    RefundDealInfo,
    RefundMethod,
    RefundSource,
    SbpBank,
    SelfEmployed,
    Settlement,
    ThreeDSecureDetails,
    Transfer,
    Webhook,
)
from .operation import Operation
from .retry import RetryPolicy
from .unknown_fields import UnknownFieldWarning

__all__ = [
    "__version__",
    # клиенты
    "AsyncYooKassa",
    "YooKassa",
    # уведомления
    "webhooks",
    # ошибки
    "APIError",
    "BadRequest",
    "ConfigurationError",
    "Forbidden",
    "Gone",
    "NotFound",
    "RateLimited",
    "ResponseProcessing",
    "ServerError",
    "TransportError",
    "Unauthorized",
    "YooKassaError",
    # предупреждения
    "UnknownFieldWarning",
    # модели
    "Amount",
    "AuthorizationDetails",
    "B2bSberbankVatData",
    "BankCardData",
    "BankCardProduct",
    "CancellationDetails",
    "Confirmation",
    "Deal",
    "DeliveryMethod",
    "ElectronicCertificate",
    "ElectronicCertificateApprovedPaymentArticle",
    "ElectronicCertificatePayment",
    "ElectronicCertificateRefundArticle",
    "ElectronicCertificateRefundData",
    "FiscalizationData",
    "IncomeReceipt",
    "IndustryDetails",
    "Invoice",
    "InvoiceDetails",
    "InvoicePaymentDetails",
    "LineItem",
    "MarkCodeInfo",
    "MarkQuantity",
    "Me",
    "OperationalDetails",
    "Page",
    "PayerBankDetails",
    "Payment",
    "PaymentDealInfo",
    "PaymentMethod",
    "PaymentMethodAlfabank",
    "PaymentMethodAlfaPay",
    "PaymentMethodApplePay",
    "PaymentMethodB2bSberbank",
    "PaymentMethodBankCard",
    "PaymentMethodCash",
    "PaymentMethodConfirmation",
    "PaymentMethodElectronicCertificate",
    "PaymentMethodGooglePay",
    "PaymentMethodInstallments",
    "PaymentMethodMobileBalance",
    "PaymentMethodQiwi",
    "PaymentMethodSberbank",
    "PaymentMethodSberBnpl",
    "PaymentMethodSberLoan",
    "PaymentMethodSbp",
    "PaymentMethodTinkoffBank",
    "PaymentMethodWebmoney",
    "PaymentMethodWeChat",
    "PaymentMethodYooMoney",
    "Payout",
    "PayoutCardData",
    "PayoutDealInfo",
    "PayoutDestination",
    "PayoutSelfEmployedInfo",
    "PersonalData",
    "PosLink",
    "PosLinkPayment",
    "Receipt",
    "ReceiptItem",
    "ReceiptItemSupplier",
    "Recipient",
    "Refund",
    "RefundAuthorizationDetails",
    "RefundDealInfo",
    "RefundMethod",
    "RefundSource",
    "SbpBank",
    "SelfEmployed",
    "Settlement",
    "ThreeDSecureDetails",
    "Transfer",
    "Webhook",
    # расширение
    "Operation",
    "RetryPolicy",
]
