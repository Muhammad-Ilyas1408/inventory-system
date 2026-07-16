# Project Folder Structure

```text
inventory_system/
│
├── .venv/
├── .gitignore
├── .python-version
├── pyproject.toml
├── README.md
├── config.py
├── main.py
│
├── docs/
│   ├── project_requirements.md
│   ├── use_cases.md
│   ├── class_diagram.md
│   ├── database_schema.md
│   └── folder_structure.md
│
├── models/
│   ├── __init__.py
│   ├── product.py
│   ├── customer.py
│   ├── order.py
│   ├── order_item.py
│   ├── invoice.py
│   └── enums.py
│
├── services/
│   ├── __init__.py
│   ├── inventory_service.py
│   ├── customer_service.py
│   ├── order_service.py
│   ├── invoice_service.py
│   ├── report_service.py
│   └── storage_service.py
│
├── utils/
│   ├── __init__.py
│   ├── validators.py
│   ├── helpers.py
│   ├── exceptions.py
│   └── constants.py
│
├── storage/
│   └── database.json
│
├── reports/
│   └── .gitkeep
│
├── logs/
│   └── .gitkeep
│
└── tests/
    ├── __init__.py
    └── .gitkeep
```

---

# Folder Responsibilities

## docs

Contains all project documentation, design documents, architecture, and planning files.

---

## models

Contains the business entities (domain models) of the application.

---

## services

Implements the business logic and coordinates operations between models and storage.

---

## storage

Stores application data. Version 1 uses a JSON file for persistence.

---

## utils

Contains reusable utilities such as validators, constants, helper functions, and custom exceptions.

---

## reports

Stores generated reports exported by the application.

---

## logs

Stores application log files.

---

## tests

Contains unit and integration tests for the project.
```