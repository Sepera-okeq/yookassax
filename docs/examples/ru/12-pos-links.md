# Кассовые ссылки

Кассовая ссылка привязывает статический QR-код к торговой точке. Покупатель
сканирует один и тот же код, а платежи приходят на нужный магазин.

* [Создание кассовой ссылки](#создание-кассовой-ссылки)
* [Информация о кассовой ссылке](#информация-о-кассовой-ссылке)
* [Активация](#активация)
* [Деактивация](#деактивация)
* [Смена торговой точки](#смена-торговой-точки)

## Создание кассовой ссылки

```python
pos_link = kassa.pos_links.create({
    "recipient": {"gateway_id": "456"},
    "pos_link_data": {
        "link": "https://qr.nspk.ru/AD100003N2S98C2U48D6N60M12345678",
    },
})

print(pos_link.id)
print(pos_link.status)   # active, inactive
```

Асинхронно:

```python
pos_link = await kassa.pos_links.create({
    "recipient": {"gateway_id": "456"},
    "pos_link_data": {
        "link": "https://qr.nspk.ru/AD100003N2S98C2U48D6N60M12345678",
    },
})
```

## Информация о кассовой ссылке

```python
pos_link = kassa.pos_links.get("pl-285e5ee7-0022-5000-8000-01516a44b147")

pos_link.status
pos_link.type
pos_link.recipient    # текущая торговая точка
pos_link.payment      # последний платёж по ссылке
```

## Активация

Включает ранее отключённую ссылку.

```python
pos_link = kassa.pos_links.activate("pl-285e5ee7-0022-5000-8000-01516a44b147")
print(pos_link.status)   # active
```

## Деактивация

Ссылка перестаёт принимать платежи, но не удаляется: её можно включить снова.

```python
pos_link = kassa.pos_links.deactivate("pl-285e5ee7-0022-5000-8000-01516a44b147")
print(pos_link.status)   # inactive
```

## Смена торговой точки

Переводит уже напечатанный QR-код на другую торговую точку.

```python
pos_link = kassa.pos_links.change_recipient(
    "pl-285e5ee7-0022-5000-8000-01516a44b147",
    {"recipient": {"gateway_id": "789"}},
)

print(pos_link.recipient)
```

Асинхронно:

```python
pos_link = await kassa.pos_links.change_recipient(
    "pl-285e5ee7-0022-5000-8000-01516a44b147",
    {"recipient": {"gateway_id": "789"}},
)
```

Метод называется `change_recipient`, а путь в API просто `/recipient`. Это не
опечатка: так в официальной спецификации.
