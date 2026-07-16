# Database Schema

Version 1 uses JSON as the persistence layer.

---

# Database Structure

```json
{
    "products": [],
    "customers": [],
    "orders": [],
    "invoices": []
}
```

---

# Product

```text
id
sku
name
category
description
price
quantity
supplier
minimum_stock
is_active
created_at
updated_at
```

---

# Customer

```text
id
name
email
phone
address
created_at
updated_at
```

---

# Order

```text
id
customer_id
items
subtotal
tax
grand_total
status
created_at
updated_at
```

---

# OrderItem

```text
product_id
product_name
quantity
unit_price
line_total
```

---

# Invoice

```text
invoice_id
order_id
customer_name
customer_phone
items
subtotal
tax
grand_total
created_at
```

---

# Relationships

Customer (1)

↓

Orders (Many)

↓

OrderItems (Many)

↓

Product (1)

↓

Invoice (1)

---

# Storage Layer

The application communicates with the JSON database only through StorageService.

No other module should directly read or write database.json.