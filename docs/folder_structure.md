# Project Folder Structure

```text
inventory_system/

│

├── main.py

├── README.md

├── requirements.txt

│

├── docs/

│      project_requirements.md

│      use_cases.md

│      class_diagram.md

│      database_schema.md

│      folder_structure.md

│

├── models/

│      product.py

│      customer.py

│      order.py

│      order_item.py

│      invoice.py

│      enums.py

│

├── services/

│      inventory_service.py

│      customer_service.py

│      order_service.py

│      invoice_service.py

│      report_service.py

│      storage_service.py

│

├── utils/

│      validators.py

│      helpers.py

│      exceptions.py

│      constants.py

│

├── storage/

│      database.json

│

├── reports/

│

├── logs/

│

└── tests/
```

---

# Folder Responsibilities

## docs

Project documentation.

---

## models

Business entities.

---

## services

Business logic.

---

## storage

Persistent data.

---

## utils

Reusable helper functions.

---

## tests

Unit tests.

---

## reports

Generated reports.

---

## logs

Application logs.