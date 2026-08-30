# Response models

Every object the API returns is parsed into a typed model. No dictionaries are
left in responses: `dict` appears only where the specification itself promises
arbitrary content (`metadata`, `holder`).

Models in total: 73. Completeness is held by tests:
`test_every_response_object_has_a_model` checks that every object appearing in a
response has a model, and `test_models_cover_documented_fields` checks that the
model declares every field the specification gives that object. A new object or
field in the specification fails the run until it is described.

* [How to read the tables](#how-to-read-the-tables)
* [Payments](#payments)
* [Refunds](#refunds)
* [Receipts](#receipts)
* [Payouts](#payouts)
* [Deals](#deals)
* [Invoices, links, self-employed](#invoices-links-self-employed)
* [Shop](#shop)
* [Shared nested objects](#shared-nested-objects)
* [Lists](#lists)

## How to read the tables

"Fields" is how many fields the model has, inherited ones included, except the
internal `raw`. An unknown field is not lost: it stays in `raw`, is reachable
through `extra()` and raises `UnknownFieldWarning` once.

## Payments

| Model | Fields | What it is |
|---|---|---|
| `B2bSberbankVatData` | 3 | НДС при оплате по счёту от юридического лица |
| `ElectronicCertificate` | 4 | Электронный сертификат, которым оплачена позиция |
| `ElectronicCertificateApprovedPaymentArticle` | 4 | Позиция корзины, одобренной к оплате сертификатом |
| `ElectronicCertificatePayment` | 2 | Данные ФЭС НСПК по оплате сертификатом |
| `InvoiceDetails` | 1 | Ссылка на счёт, по которому прошёл платёж |
| `Payment` | 23 | Платёж |
| `PaymentDealInfo` | 2 | Сделка, в составе которой идёт платёж |
| `PaymentMethod` | 14 | Способ оплаты |
| `PaymentMethodAlfaPay` | 14 | Alfa Pay |
| `PaymentMethodAlfabank` | 14 | Альфа-Клик |
| `PaymentMethodApplePay` | 14 | Apple Pay |
| `PaymentMethodB2bSberbank` | 16 | Сбербанк Бизнес Онлайн: оплата по счёту от юридического лица |
| `PaymentMethodBankCard` | 14 | Банковская карта |
| `PaymentMethodCash` | 14 | Наличные |
| `PaymentMethodConfirmation` | 5 | Подтверждение привязки способа оплаты |
| `PaymentMethodElectronicCertificate` | 16 | Электронный сертификат: карта «Мир» с сертификатом ФСС |
| `PaymentMethodGooglePay` | 14 | Google Pay |
| `PaymentMethodInstallments` | 14 | Заплатить по частям |
| `PaymentMethodMobileBalance` | 14 | Баланс телефона |
| `PaymentMethodQiwi` | 14 | QIWI Кошелёк |
| `PaymentMethodSberBnpl` | 14 | Оплата частями от СберБанка |
| `PaymentMethodSberLoan` | 17 | Кредит или рассрочка от СберБанка |
| `PaymentMethodSberbank` | 14 | СберБанк Онлайн |
| `PaymentMethodSbp` | 14 | Система быстрых платежей |
| `PaymentMethodTinkoffBank` | 14 | Т-Банк |
| `PaymentMethodWeChat` | 14 | WeChat Pay |
| `PaymentMethodWebmoney` | 14 | WebMoney |
| `PaymentMethodYooMoney` | 14 | Кошелёк ЮMoney |

## Refunds

| Model | Fields | What it is |
|---|---|---|
| `ElectronicCertificateRefundArticle` | 4 | Позиция корзины возврата на электронный сертификат |
| `ElectronicCertificateRefundData` | 2 | Данные ФЭС НСПК для возврата на электронный сертификат |
| `Refund` | 13 | Возврат денег плательщику |
| `RefundAuthorizationDetails` | 1 | Данные авторизации возврата |
| `RefundDealInfo` | 2 | Сделка, в составе которой идёт возврат |
| `RefundMethod` | 4 | Детали возврата: зависят от способа, которым платили |
| `RefundSource` | 3 | С какого магазина и сколько удержать при возврате в маркетплейсе |

## Receipts

| Model | Fields | What it is |
|---|---|---|
| `IndustryDetails` | 4 | Отраслевой реквизит (тег 1260) |
| `MarkCodeInfo` | 11 | Код маркировки товара (тег 1163) |
| `MarkQuantity` | 2 | Дробное количество маркированного товара (тег 1291) |
| `OperationalDetails` | 3 | Операционный реквизит чека (тег 1270) |
| `Receipt` | 19 | Чек, зарегистрированный в налоговой |
| `ReceiptItem` | 18 | Позиция чека |
| `ReceiptItemSupplier` | 3 | Поставщик товара или услуги (тег 1224) |

## Payouts

| Model | Fields | What it is |
|---|---|---|
| `IncomeReceipt` | 4 | Чек самозанятого, зарегистрированный в налоговой |
| `Payout` | 13 | Выплата |
| `PayoutCardData` | 5 | Карта, на которую ушла выплата |
| `PayoutDealInfo` | 1 | Сделка, в рамках которой проведена выплата |
| `PayoutDestination` | 7 | Куда ушла выплата |
| `PayoutSelfEmployedInfo` | 1 | Самозанятый, получивший выплату |

## Deals

| Model | Fields | What it is |
|---|---|---|
| `Deal` | 11 | Сделка: держит деньги до выполнения обязательств продавцом |

## Invoices, links, self-employed

| Model | Fields | What it is |
|---|---|---|
| `DeliveryMethod` | 2 | Способ доставки счёта плательщику |
| `Invoice` | 10 | Счёт на оплату |
| `InvoicePaymentDetails` | 2 | Платёж по счёту. Появляется, когда счёт оплачен |
| `LineItem` | 4 | Позиция корзины счёта |
| `PersonalData` | 7 | Персональные данные получателя выплаты |
| `PosLink` | 5 | Ссылка на оплату в кассе |
| `PosLinkPayment` | 2 | Последний платёж по кассовой ссылке |
| `SbpBank` | 3 | Банк из справочника СБП |
| `SelfEmployed` | 9 | Самозанятый получатель выплат |

## Shop

| Model | Fields | What it is |
|---|---|---|
| `FiscalizationData` | 2 | Настройки отправки чеков в налоговую |
| `Me` | 10 | Ответ GET /me: кто мы для ЮKassa |
| `Webhook` | 3 | Подписка на уведомление |

## Shared nested objects

| Model | Fields | What it is |
|---|---|---|
| `Amount` | 2 | Сумма и валюта |
| `AuthorizationDetails` | 3 | Данные авторизации карточного платежа |
| `BankCardData` | 9 | Данные банковской карты |
| `BankCardProduct` | 2 | Карточный продукт платёжной системы, например Mir Supreme |
| `CancellationDetails` | 2 | Кто и почему отменил операцию |
| `Confirmation` | 6 | Сценарий подтверждения: как довести плательщика до оплаты |
| `PayerBankDetails` | 11 | Реквизиты счёта плательщика |
| `Recipient` | 2 | Получатель платежа: магазин и шлюз |
| `Settlement` | 2 | Расчёт: сколько и на что распределено внутри операции |
| `ThreeDSecureDetails` | 1 | Прошла ли аутентификация 3-D Secure |
| `Transfer` | 8 | Часть платежа, уходящая отдельному продавцу в маркетплейсе |

## Lists

| Model | Fields | What it is |
|---|---|---|
| `Page` | 3 | Страница списка: элементы плюс курсор на следующую |

## What is deliberately absent

**Models for request bodies.** A request body is a plain dictionary: it accepts
new API fields immediately, not after a library release. In the specification
these are the schemas suffixed `Data` and `Request` - `PaymentMethodDataBankCard`,
`PayoutRequest` and the like.

**A separate class per synonym schema.** YooKassa names identically shaped
objects differently in each resource: `SettlementPaymentItem`,
`SettlementRefundItem`, `SettlementPayoutPayment` are all the same
`{type, amount}`. Such schemas share one model; the mapping lives in the test as
`SCHEMA_TO_MODEL`.

**Models for errors.** An error response is raised as an exception rather than
returned as an object: `BadRequest`, `Forbidden` and the rest carry `code`,
`description`, `parameter` and `request_id`.
