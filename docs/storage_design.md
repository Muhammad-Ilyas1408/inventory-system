# Storage Layer Design

## Purpose

The Storage Layer is responsible for persisting application data.

Its sole responsibility is reading and writing data to persistent storage.

For Version 1, persistent storage is implemented using a JSON file.

The Storage Layer is intentionally designed to remain independent of business rules. This allows the storage implementation to be replaced in the future (e.g., SQLite, PostgreSQL, or another database) without requiring changes to the business services.

---

# Responsibilities

The StorageService is responsible for:

- Creating the database file if it does not exist.
- Loading data from the JSON database.
- Saving data to the JSON database.
- Ensuring the database follows the expected JSON structure.
- Handling file-related operations.
- Returning plain Python dictionaries.

The StorageService is **not** responsible for:

- Product validation.
- Customer validation.
- Order validation.
- Invoice validation.
- Business rules.
- Inventory management.
- Searching records.
- Generating IDs.
- Order processing.
- Invoice generation.

These responsibilities belong to the Business Service layer.

---

# Public API

Version 1 exposes a minimal public interface.

## initialize_database()

### Purpose

Create the database file if it does not already exist.

### Responsibilities

- Check whether the database file exists.
- Create the file if missing.
- Write the default database schema.
- Never overwrite an existing database.

---

## load_data()

### Purpose

Load the complete database into memory.

### Returns

```python
dict[str, list]
```

### Responsibilities

- Open the JSON file.
- Parse the JSON.
- Return the complete database as a Python dictionary.

---

## save_data(data)

### Purpose

Persist the application's current state.

### Parameters

```python
data: dict
```

### Responsibilities

- Serialize the dictionary into JSON.
- Save the JSON file.
- Preserve readable formatting.

The StorageService never modifies the supplied data.

---

# Database Schema

Version 1 stores all data inside a single JSON file.

```json
{
    "products": [],
    "customers": [],
    "orders": [],
    "invoices": []
}
```

Each collection stores serialized dictionaries produced by the corresponding model's `to_dict()` method.

Example:

```json
{
    "products": [
        {
            "id": "PROD001",
            "name": "Laptop",
            "category": "Electronics",
            "price": 1200.0,
            "quantity": 15,
            "supplier": "Dell",
            "created_at": "...",
            "updated_at": "..."
        }
    ],
    "customers": [],
    "orders": [],
    "invoices": []
}
```

---

# Data Flow

## Reading Data

```text
User
    │
    ▼
CLI
    │
    ▼
Business Service
    │
    ▼
StorageService.load_data()
    │
    ▼
database.json
```

---

## Writing Data

```text
User
    │
    ▼
CLI
    │
    ▼
Business Service
    │
    ▼
StorageService.save_data()
    │
    ▼
database.json
```

StorageService never decides **what** should be saved.

It only knows **how** to save data.

---

# Error Handling Strategy

## Missing Database File

Handled by:

StorageService

Action:

Create a new database using the default schema.

---

## Empty Database File

Handled by:

StorageService

Action:

Raise an exception because an empty file is not valid JSON.

---

## Invalid JSON

Handled by:

StorageService

Action:

Raise an exception.

The application should never silently recreate or overwrite corrupted data because doing so could cause permanent data loss.

---

## File Permission Errors

Handled by:

StorageService

Action:

Propagate the exception so the application can report the failure to the user.

---

## Business Errors

Examples:

- Duplicate Product ID
- Product Not Found
- Customer Not Found
- Insufficient Stock

Handled by:

Business Services

StorageService should never contain business logic.

---

# Separation of Responsibilities

## Models

Responsible for:

- Data representation
- Validation
- Serialization (`to_dict`)
- Deserialization (`from_dict`)

---

## StorageService

Responsible for:

- Reading JSON
- Writing JSON
- Creating the database
- File management

---

## Business Services

Responsible for:

- CRUD operations
- Business rules
- Inventory management
- Customer management
- Order processing
- Invoice generation
- Cross-entity validation

---

# Design Decisions

## Why return dictionaries instead of model objects?

StorageService should remain generic.

It should not depend on Product, Customer, Order, or Invoice.

Business Services are responsible for converting dictionaries into model objects using the corresponding `from_dict()` methods.

---

## Why only three public methods?

A minimal public API keeps the Storage Layer simple and maintainable.

All business logic remains inside the Business Service layer.

StorageService only persists application data.

---

## Why separate storage from business logic?

Separating persistence from business logic makes the application easier to maintain, test, and extend.

If the storage backend changes in the future, the Business Services should continue working without modification.

---

# Storage Layer Principles

The Storage Layer follows these software engineering principles.

## Single Responsibility Principle (SRP)

StorageService has exactly one responsibility:

Persist application data.

---

## Separation of Concerns

Persistence logic is isolated from business logic.

Business Services decide **what** should happen.

StorageService only persists the result.

---

## Low Coupling

StorageService does not depend on Product, Customer, Order, or Invoice classes.

This minimizes dependencies between application layers.

---

## High Cohesion

All file persistence logic exists in one dedicated module.

No other part of the application should directly read or write `database.json`.

---

## Replaceability

The storage implementation can be replaced without changing the Business Services.

Possible future implementations include:

- SQLite
- PostgreSQL
- MongoDB
- Cloud databases

---

# Future Extensibility

The architecture intentionally isolates the persistence layer.

Future enhancements may include:

- SQLite support
- PostgreSQL support
- Database transactions
- Connection pooling
- Automatic backups
- Data encryption
- Repository pattern
- Cloud storage
- Database migrations

The Business Services and Models should require little or no modification when these improvements are introduced.

---

# Version 1 Limitations

Version 1 intentionally keeps the storage implementation simple.

Known limitations include:

- Single JSON file
- No concurrent access
- No transactions
- No indexing
- No automatic backups
- No caching

These limitations are acceptable for a learning project and provide a solid foundation for future versions.

---

# Summary

The Storage Layer exists solely to persist application data.

It intentionally contains no business logic and exposes a minimal public interface.

This separation of responsibilities results in a clean, maintainable, and extensible architecture that can evolve from JSON-based storage to a full database backend with minimal changes to the rest of the application.