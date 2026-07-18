"""Unit tests for the JSON-backed storage service."""

import json
from pathlib import Path

import pytest

import services.storage_service as storage_service
from services.storage_service import StorageService


@pytest.fixture
def database_path(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Configure StorageService to use an isolated temporary database."""
    path = tmp_path / "database.json"
    monkeypatch.setattr(storage_service, "DATABASE_PATH", path)
    return path


def create_valid_data() -> dict[str, list]:
    """Return valid database data for storage tests."""
    return {
        "products": [{"id": "PROD001", "name": "Laptop"}],
        "customers": [{"id": "CUST001", "name": "Ada Lovelace"}],
        "orders": [{"id": "ORD001"}],
        "invoices": [{"id": "INV001"}],
    }


def test_initialize_database_creates_file_with_default_schema(
    database_path: Path,
) -> None:
    """Initialize a missing database using the default schema."""
    service = StorageService()

    service.initialize_database()

    assert database_path.exists()
    with database_path.open(encoding="utf-8") as database_file:
        assert json.load(database_file) == service.DEFAULT_SCHEMA


def test_load_data_returns_valid_database(database_path: Path) -> None:
    """Load a valid database without modifying its contents."""
    expected_data = create_valid_data()
    with database_path.open("w", encoding="utf-8") as database_file:
        json.dump(expected_data, database_file)

    loaded_data = StorageService().load_data()

    assert loaded_data == expected_data


def test_save_data_persists_valid_database(database_path: Path) -> None:
    """Save valid database data using readable JSON."""
    expected_data = create_valid_data()

    StorageService().save_data(expected_data)

    with database_path.open(encoding="utf-8") as database_file:
        assert json.load(database_file) == expected_data


def test_load_data_initializes_missing_database(database_path: Path) -> None:
    """Create and load the default database when the file is missing."""
    service = StorageService()

    loaded_data = service.load_data()

    assert database_path.exists()
    assert loaded_data == service.DEFAULT_SCHEMA


def test_load_data_raises_for_invalid_json(database_path: Path) -> None:
    """Propagate JSON parsing errors for malformed database content."""
    database_path.write_text('{"products":', encoding="utf-8")

    with pytest.raises(json.JSONDecodeError):
        StorageService().load_data()


@pytest.mark.parametrize("invalid_data", [[], 123, "hello"])
def test_load_data_raises_for_non_dictionary_top_level(
    database_path: Path,
    invalid_data: object,
) -> None:
    """Reject parsed JSON whose top-level value is not a dictionary."""
    with database_path.open("w", encoding="utf-8") as database_file:
        json.dump(invalid_data, database_file)

    with pytest.raises(ValueError, match="top-level JSON object"):
        StorageService().load_data()


def test_load_data_raises_for_missing_collection(database_path: Path) -> None:
    """Reject a database that omits a required collection."""
    invalid_data = create_valid_data()
    del invalid_data["customers"]
    with database_path.open("w", encoding="utf-8") as database_file:
        json.dump(invalid_data, database_file)

    with pytest.raises(ValueError, match="unexpected or missing"):
        StorageService().load_data()


def test_load_data_raises_for_extra_collection(database_path: Path) -> None:
    """Reject a database that contains an unexpected collection."""
    invalid_data = create_valid_data()
    invalid_data["metadata"] = []
    with database_path.open("w", encoding="utf-8") as database_file:
        json.dump(invalid_data, database_file)

    with pytest.raises(ValueError, match="unexpected or missing"):
        StorageService().load_data()


def test_load_data_raises_when_collection_is_not_a_list(
    database_path: Path,
) -> None:
    """Reject a database whose collection value is not a list."""
    invalid_data = create_valid_data()
    invalid_data["products"] = {}
    with database_path.open("w", encoding="utf-8") as database_file:
        json.dump(invalid_data, database_file)

    with pytest.raises(ValueError, match="all collections must be lists"):
        StorageService().load_data()


def test_save_data_raises_for_invalid_schema(database_path: Path) -> None:
    """Reject invalid database data before writing it to storage."""
    invalid_data = create_valid_data()
    invalid_data["products"] = {}

    with pytest.raises(ValueError, match="all collections must be lists"):
        StorageService().save_data(invalid_data)

    assert not database_path.exists()
