# InventoryService Design

> **Note:** This document defines the design and responsibilities of the InventoryService. It describes the service's role within the application architecture, its public interface, validation strategy, interaction with other components, and future extensibility.

---

# Purpose

The InventoryService is responsible for managing all product-related business operations.

It acts as the business layer between:

- Domain Models (`Product`)
- Persistent Storage (`StorageService`)
- User Interface (CLI)

The InventoryService applies business rules before data is stored or retrieved. It never performs direct file operations and never interacts with the user interface.

---

# Responsibilities

InventoryService is responsible for:

- Managing products
- Validating business rules
- Coordinating with StorageService
- Creating Product model instances
- Updating inventory quantities
- Searching products
- Returning domain objects to callers

InventoryService is **not** responsible for:

- Reading or writing JSON files directly
- Performing CLI input/output
- Managing customer data
- Processing orders
- Generating invoices

---

# Public API

Version 1 will provide the following public methods.

| Method | Description |
|---------|-------------|
| `add_product()` | Add a new product |
| `get_product_by_id()` | Retrieve a product by its ID |
| `get_all_products()` | Return all products |
| `update_product()` | Update an existing product |
| `delete_product()` | Delete a product |
| `update_stock()` | Increase or decrease inventory quantity |
| `product_exists()` | Check whether a product ID already exists |

---

# Business Rules

InventoryService enforces business rules that cannot be validated by the Product model alone.

Examples include:

- Product IDs must be unique.
- Products cannot be added twice.
- A product must exist before it can be updated.
- A product must exist before it can be deleted.
- Inventory quantity must never become negative.
- Deleted products cannot be accessed.

These rules belong to the service layer because they depend on the current state of the application's data rather than on a single Product instance.

---

# Validation Responsibilities

## Product Model

The Product model validates:

- Required fields
- Data types
- Numeric ranges
- Timestamp types

## InventoryService

InventoryService validates:

- Duplicate product IDs
- Product existence
- Inventory availability
- Business workflow rules

This separation follows the Single Responsibility Principle.

---

# Data Flow

Adding a product follows this workflow:

```text
User
        │
        ▼
InventoryService
        │
        ▼
Validate Business Rules
        │
        ▼
Create Product
        │
        ▼
StorageService.load_data()
        │
        ▼
Append Product
        │
        ▼
StorageService.save_data()
        │
        ▼
Return Product
```

Updating inventory follows this workflow:

```text
User
        │
        ▼
InventoryService
        │
        ▼
Load Database
        │
        ▼
Locate Product
        │
        ▼
Validate Stock Update
        │
        ▼
Modify Product
        │
        ▼
Save Database
```

---

# Interaction with StorageService

InventoryService depends on StorageService for persistence.

StorageService provides:

- `load_data()`
- `save_data()`

InventoryService never:

- Opens files
- Reads JSON directly
- Writes JSON directly
- Knows where the database file is located

This keeps persistence isolated from business logic.

---

# Interaction with Product Model

InventoryService creates Product objects from user data.

When loading products from storage:

```text
JSON Dictionary
        │
        ▼
Product.from_dict()
        │
        ▼
Product Object
```

When saving products:

```text
Product Object
        │
        ▼
Product.to_dict()
        │
        ▼
JSON Dictionary
```

This ensures validation remains inside the Product model.

---

# Error Handling Strategy

InventoryService should raise meaningful exceptions for business rule violations.

Examples include:

- Duplicate product ID
- Product not found
- Invalid stock adjustment
- Negative inventory

Storage-related exceptions raised by StorageService should be allowed to propagate unless the service has a specific recovery strategy.

No exceptions should be silently ignored.

---

# Design Principles

InventoryService follows these principles:

- Single Responsibility Principle (SRP)
- Separation of Concerns
- Dependency on StorageService for persistence
- Business rules isolated from models
- Readable and maintainable implementation
- Predictable public API

---

# Future Extensibility

The service should be designed so future features can be added without major refactoring.

Potential enhancements include:

- Product categories
- Product search by name
- Barcode support
- SKU generation
- Supplier management
- Low-stock alerts
- Inventory transactions
- Bulk import/export
- Database backend replacement (SQLite/PostgreSQL)
- REST API integration

---

# Out of Scope (Version 1)

The following features are intentionally excluded from Version 1:

- Product image management
- Barcode scanning
- Inventory history
- Purchase orders
- Supplier contracts
- Batch inventory updates
- Product variants
- Multi-warehouse inventory
- Role-based permissions

These may be implemented in future versions without changing the overall architecture.

---

# Summary

InventoryService is the business layer responsible for all product-related operations. It coordinates between the Product model and StorageService while enforcing business rules and maintaining a clean separation of concerns.

By isolating business logic from persistence and presentation, the service remains maintainable, testable, and extensible as the application grows.