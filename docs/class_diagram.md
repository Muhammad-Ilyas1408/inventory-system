# Inventory & Order Management System

# Final Architecture & Class Diagram (Version 1)

---

# High-Level Architecture

```text
                                   User
                                     │
                                     ▼
                              Inventory CLI
                                (main.py)
                                     │
                                     ▼
+--------------------------------------------------------------------------+
|                             Service Layer                                |
+--------------------------------------------------------------------------+
| InventoryService | CustomerService | OrderService | InvoiceService       |
| ReportService    | StorageService                                |
+-----------+---------------+---------------+---------------+--------------+
            │               │               │               │
            ▼               ▼               ▼               ▼
+--------------------------------------------------------------------------+
|                              Domain Models                               |
+--------------------------------------------------------------------------+
| Product | Customer | Order | OrderItem | Invoice | OrderStatus (Enum)    |
+--------------------------------------------------------------------------+
                                     │
                                     ▼
                             storage/database.json
```

---

# Domain Model Diagram

```text
                               +--------------------+
                               |      Product       |
                               +--------------------+
                               | id                 |
                               | sku                |
                               | name               |
                               | category           |
                               | description        |
                               | price              |
                               | quantity           |
                               | supplier           |
                               | minimum_stock      |
                               | is_active          |
                               | created_at         |
                               | updated_at         |
                               +--------------------+
                               | increase_stock()   |
                               | decrease_stock()   |
                               | to_dict()          |
                               | from_dict()        |
                               +--------------------+


                               +--------------------+
                               |     Customer       |
                               +--------------------+
                               | id                 |
                               | name               |
                               | email              |
                               | phone              |
                               | address            |
                               | created_at         |
                               | updated_at         |
                               +--------------------+
                               | update()           |
                               | to_dict()          |
                               | from_dict()        |
                               +--------------------+


                     Customer (1)
                          │
                          │ places
                          │
                          ▼

                               +--------------------+
                               |       Order        |
                               +--------------------+
                               | id                 |
                               | customer_id        |
                               | items[]            |
                               | subtotal           |
                               | tax                |
                               | grand_total        |
                               | status             |
                               | created_at         |
                               | updated_at         |
                               +--------------------+
                               | add_item()         |
                               | remove_item()      |
                               | to_dict()          |
                               | from_dict()        |
                               +---------+----------+
                                         │
                                         │ contains many
                                         ▼

                              +----------------------+
                              |      OrderItem       |
                              +----------------------+
                              | product_id           |
                              | product_name         |
                              | quantity             |
                              | unit_price           |
                              | line_total           |
                              +----------------------+

                                         │
                                         │ references
                                         ▼

                                   Product (1)



                     Order (1)
                         │
                         │ generates
                         ▼

                               +--------------------+
                               |      Invoice       |
                               +--------------------+
                               | invoice_id         |
                               | order_id           |
                               | customer_name      |
                               | customer_phone     |
                               | items[]            |
                               | subtotal           |
                               | tax                |
                               | grand_total        |
                               | created_at         |
                               +--------------------+
                               | to_dict()          |
                               | from_dict()        |
                               +--------------------+


                       +--------------------------+
                       |      OrderStatus         |
                       +--------------------------+
                       | PENDING                  |
                       | CONFIRMED                |
                       | COMPLETED                |
                       | CANCELLED                |
                       +--------------------------+
```

---

# Layer Responsibilities

## CLI Layer

### main.py

Responsibilities

- Display menus
- Read user input
- Display results
- Call appropriate service

Never

- Read JSON
- Calculate tax
- Reduce stock
- Validate business rules

---

## Service Layer

### InventoryService

Responsible for

- Add Product
- Update Product
- Delete Product
- Search Product
- Increase Stock
- Decrease Stock
- Low Stock Validation

Uses

- Product
- StorageService
- Validators
- Helpers

---

### CustomerService

Responsible for

- Add Customer
- Update Customer
- Delete Customer
- Search Customer

Uses

- Customer
- StorageService

---

### OrderService

Responsible for

- Create Order
- Validate Customer
- Validate Products
- Validate Stock
- Create OrderItems
- Calculate Subtotal
- Calculate Tax
- Calculate Grand Total
- Reduce Inventory
- Save Order

Uses

- Product
- Customer
- Order
- OrderItem
- StorageService

---

### InvoiceService

Responsible for

- Generate Invoice
- Save Invoice
- Print Invoice

Uses

- Order
- Invoice
- StorageService

---

### ReportService

Responsible for

- Sales Report
- Inventory Report
- Customer Report
- Low Stock Report
- Best Selling Products

Uses

- Product
- Customer
- Order
- Invoice

---

### StorageService

Responsible for

- Load Database
- Save Database
- Backup Database

Never

- Validate Business Rules
- Calculate Totals
- Generate IDs
- Generate Reports

---

## Domain Models

### Product

Represents a product sold by the business.

Knows

- Product information
- Stock operations
- Serialization

Never

- Save itself
- Read JSON
- Print menus

---

### Customer

Represents a customer.

Knows

- Customer information
- Update information
- Serialization

Never

- Create Orders
- Read JSON

---

### Order

Represents a customer purchase.

Knows

- Customer ID
- Order Items
- Current Status

Never

- Reduce inventory
- Calculate business discounts
- Save itself

---

### OrderItem

Represents one product inside an order.

Stores

- Product purchased
- Quantity purchased
- Purchase price
- Line total

Purpose

Preserves historical purchase information.

---

### Invoice

Represents proof of purchase.

Stores

- Customer snapshot
- Purchased items
- Purchase prices
- Order reference

Purpose

Acts as a permanent historical record.

---

### OrderStatus

Represents the lifecycle of an order.

Possible values

- PENDING
- CONFIRMED
- COMPLETED
- CANCELLED

Using an Enum prevents invalid status values.

---

## Utility Layer

Contains

- validators.py
- helpers.py
- exceptions.py
- constants.py

Responsibilities

- Validate Email
- Validate Phone
- Validate Price
- Validate Quantity
- Generate UUID
- Generate Timestamp
- Format Currency
- Custom Exceptions

---

# Complete Request Flow

```text
User
 │
 ▼
Inventory CLI (main.py)
 │
 ▼
Service Layer
 │
 ▼
Validation
 │
 ▼
Create Domain Object
 │
 ▼
StorageService
 │
 ▼
database.json
 │
 ▼
Success Response
```

---

# Design Principles

## Separation of Concerns

- CLI handles user interaction.
- Services handle business logic.
- Models represent business entities.
- Storage handles persistence.
- Utilities provide reusable functionality.

---

## Single Responsibility Principle (SRP)

Every module has one clear responsibility.

---

## High Cohesion

Each class contains closely related functionality.

---

## Low Coupling

Modules communicate through services and avoid unnecessary dependencies.

---

## Extensibility

Future upgrades require minimal changes.

Possible Version 2 improvements:

- SQLite
- PostgreSQL
- FastAPI REST API
- Authentication
- Barcode Support
- Docker
- Cloud Deployment

The business logic and domain models remain unchanged.