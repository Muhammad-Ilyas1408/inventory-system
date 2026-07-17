# Engineering Guidelines

> **Note:** These guidelines define the engineering standards for this project. They are intended for both human contributors and development tools, including AI assistants, to ensure consistent code quality, maintainability, and architectural consistency across the entire codebase.

---

## Purpose

This document defines the engineering standards, architectural principles, coding conventions, and development workflow used throughout this project.

The goal is to ensure that every module follows the same design principles, resulting in a codebase that is consistent, maintainable, readable, and easy to extend.

---

# Project Information

**Project Name**

Inventory & Order Management System

**Language**

Python 3.11

**Application Type**

Command-Line Interface (CLI)

**Architecture**

Layered Architecture

**Current Storage**

JSON File

---

# Architecture Principles

The project follows a layered architecture where every module has a single responsibility.

```text
User
   │
   ▼
CLI (main.py)
   │
   ▼
Services
   │
   ▼
Models
   │
   ▼
StorageService
   │
   ▼
JSON Database
```

## Models

Models represent business entities.

### Responsibilities

- Store application data
- Validate their own data
- Serialize to dictionaries
- Deserialize from dictionaries

### Models must NOT

- Perform file I/O
- Read or write JSON
- Import Services
- Contain business workflows
- Contain application logic

---

## Services

Services contain the business logic of the application.

### Responsibilities

- Coordinate operations
- Apply business rules
- Validate workflows
- Communicate with `StorageService`

### Services must NOT

- Handle CLI input/output
- Store business data permanently

---

## Storage

Storage is responsible only for persistence.

### Responsibilities

- Read JSON
- Write JSON
- Save data
- Load data

Storage must not contain business logic.

---

## Utils

Utility modules contain reusable components such as:

- Validators
- Constants
- Helper functions
- Custom Exceptions

Utilities should remain generic and reusable.

---

# Object-Oriented Programming Principles

- Every class should have a single responsibility.
- Prefer composition over unnecessary inheritance.
- Avoid global state.
- Keep classes cohesive.
- Keep methods focused on one task.

---

# Coding Standards

Follow:

- Python 3.11
- PEP 8
- Maximum line length: 88 characters
- Explicit type hints
- Google-style docstrings
- Clear variable names
- Descriptive method names
- Small functions
- Small classes

### General Principles

- Prioritize readability over cleverness.
- Avoid unnecessary abstraction.
- Do not over-engineer solutions.
- Keep code easy to understand and maintain.

---

# Type Hints

Use type hints throughout the project.

Examples:

```python
name: str
price: float
quantity: int

def add_product(product: Product) -> None:
    ...

def to_dict(self) -> dict[str, Any]:
    ...
```

Avoid untyped public methods.

---

# Documentation

Every public class should contain a docstring.

Every public method should contain a Google-style docstring.

Docstrings should explain:

- Purpose
- Arguments
- Returns
- Raised exceptions (when applicable)

Keep documentation concise.

---

# Comments

Comments should explain **WHY**, not **WHAT**.

Good:

```python
# Normalize whitespace to ensure consistent data storage.
```

Avoid:

```python
# Increment quantity by one.
quantity += 1
```

Do not comment obvious code.

---

# Validation

Validate user-provided data as early as possible.

Model validation belongs inside `__post_init__()`.

Raise meaningful exceptions.

Normalize data whenever appropriate.

Examples:

- Strip whitespace
- Convert numeric types
- Validate timestamps
- Check required fields

---

# Error Handling

- Raise meaningful exceptions.
- Never silently ignore errors.
- Use custom exceptions where appropriate.
- Error messages should help identify the actual problem.

---

# Serialization

Models that are stored in JSON should provide:

- `to_dict()`
- `from_dict()`

Datetime objects should be serialized using:

```python
datetime.isoformat()
```

Deserialize using:

```python
datetime.fromisoformat()
```

---

# Business Logic

Business rules belong inside Services.

Examples:

- Placing an order
- Updating inventory
- Generating invoices
- Calculating totals
- Validating stock availability

Business logic should never exist inside Models.

---

# File Organization

- Each file should have one clear responsibility.
- Avoid extremely large files.
- Related functionality should remain together.

---

# Git Workflow

Use small, focused commits.

Good examples:

```text
Implement Product model

Implement Customer model

Implement StorageService

Implement InventoryService CRUD operations

Add CLI menu

Write Product unit tests
```

Avoid commit messages such as:

```text
Update

Changes

Fix

Final

Done
```

### Workflow

- Commit frequently.
- Push regularly.
- Keep the `main` branch in a working state.

---

# Testing

Write tests for:

- Model validation
- Business logic
- Storage layer
- Edge cases

Prefer many small tests over one large test.

---

# Performance

- Prefer clean and maintainable code first.
- Optimize only after identifying an actual performance problem.
- Avoid premature optimization.

---

# Code Review Checklist

Before committing code, verify:

- Architecture is respected.
- Responsibilities are clear.
- No duplicated logic.
- Type hints are complete.
- Validation is present.
- Exceptions are meaningful.
- Docstrings are written.
- Comments explain **WHY**.
- Code follows PEP 8.
- The module remains readable.

---

# Development Philosophy

This project emphasizes software engineering practices over simply making the application work.

Every feature should be:

- Planned before implementation.
- Designed with maintainability in mind.
- Easy to understand.
- Easy to test.
- Easy to extend.

The objective is to build a portfolio-quality project that demonstrates clean architecture, professional Python development, and sound software engineering principles.