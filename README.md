# Inventory & Order Management System

A modular Command-Line Inventory & Order Management System built with Python.

This project implements a layered software architecture and applies object-oriented programming, data validation, exception handling, JSON-based persistence, and clean software engineering principles.

> **Project Status:** Under Development (Version 0.1.0)

---

## Table of Contents

- [Features](#features)
- [Project Goals](#project-goals)
- [Tech Stack](#tech-stack)
- [Installation](#installation)
- [Project Structure](#project-structure)
- [Development Roadmap](#development-roadmap)
- [Future Improvements](#future-improvements)
- [License](#license)

---

## Features

### Planned Features

- Product Management
- Customer Management
- Inventory Management
- Order Processing
- Invoice Generation
- Sales Reporting
- JSON-based Data Storage
- Input Validation
- Custom Exceptions
- Modular Architecture

---

## Project Goals

The primary goals of this project are to:

- Apply Object-Oriented Programming (OOP)
- Build a modular Python application
- Design a maintainable software architecture
- Practice CRUD operations
- Implement business logic
- Work with JSON file storage
- Follow software engineering best practices
- Build a portfolio-quality project

---

## Tech Stack

- Python 3.11
- uv
- Git
- GitHub
- JSON

---

## Installation

### Clone the repository

```bash
git clone https://github.com/Muhammad-Ilyas1408/inventory-system.git
```

### Navigate to the project

```bash
cd inventory-system
```

### Create a virtual environment

```bash
uv venv
```

### Activate the virtual environment

**Windows**

```bash
.venv\Scripts\activate
```

**Linux / macOS**

```bash
source .venv/bin/activate
```

### Install project dependencies

```bash
uv sync
```

> **Note:** No external dependencies have been added yet. Dependencies will be managed using `uv` as the project grows.

---

## Project Structure

```text
inventory_system/
│
├── docs/
├── models/
├── services/
├── storage/
├── utils/
├── tests/
├── reports/
├── logs/
│
├── main.py
├── config.py
├── pyproject.toml
└── README.md
```

---

## Development Roadmap

### Project Setup

- [x] Project Planning
- [x] Software Architecture Design
- [x] Project Documentation
- [x] Folder Structure
- [x] Git Setup
- [x] GitHub Repository

### Core Development

- [ ] Product Model
- [ ] Customer Model
- [ ] Order Model
- [ ] Invoice Model
- [ ] JSON Storage Layer
- [ ] Inventory Service
- [ ] Customer Service
- [ ] Order Service
- [ ] Invoice Service
- [ ] Reporting Service

### User Interface

- [ ] Command-Line Interface (CLI)

### Quality Assurance

- [ ] Unit Tests
- [ ] Integration Tests
- [ ] Documentation Updates

---

## Future Improvements

Future versions may include:

- SQLite Support
- PostgreSQL Support
- REST API using FastAPI
- User Authentication
- Barcode Scanner Integration
- Docker Support
- Cloud Deployment

---

## License

This project is intended for educational and portfolio purposes.