# POS links

A POS link binds a static QR code to a point of sale. The buyer scans the same
code while payments arrive at the right shop.

* [Creating a POS link](#creating-a-pos-link)
* [POS link details](#pos-link-details)
* [Activation](#activation)
* [Deactivation](#deactivation)
* [Changing the point of sale](#changing-the-point-of-sale)

## Creating a POS link

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

Asynchronously:

```python
pos_link = await kassa.pos_links.create({
    "recipient": {"gateway_id": "456"},
    "pos_link_data": {
        "link": "https://qr.nspk.ru/AD100003N2S98C2U48D6N60M12345678",
    },
})
```

## POS link details

```python
pos_link = kassa.pos_links.get("pl-285e5ee7-0022-5000-8000-01516a44b147")

pos_link.status
pos_link.type
pos_link.recipient    # current point of sale
pos_link.payment      # the latest payment through the link
```

## Activation

Turns a previously disabled link back on.

```python
pos_link = kassa.pos_links.activate("pl-285e5ee7-0022-5000-8000-01516a44b147")
print(pos_link.status)   # active
```

## Deactivation

The link stops accepting payments but is not deleted: it can be switched on
again.

```python
pos_link = kassa.pos_links.deactivate("pl-285e5ee7-0022-5000-8000-01516a44b147")
print(pos_link.status)   # inactive
```

## Changing the point of sale

Moves an already printed QR code to a different point of sale.

```python
pos_link = kassa.pos_links.change_recipient(
    "pl-285e5ee7-0022-5000-8000-01516a44b147",
    {"recipient": {"gateway_id": "789"}},
)

print(pos_link.recipient)
```

Asynchronously:

```python
pos_link = await kassa.pos_links.change_recipient(
    "pl-285e5ee7-0022-5000-8000-01516a44b147",
    {"recipient": {"gateway_id": "789"}},
)
```

The method is called `change_recipient` while the API path is simply
`/recipient`. That is not a typo: it matches the official specification.
