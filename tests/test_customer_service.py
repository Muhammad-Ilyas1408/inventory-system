"""Unit tests for customer-related service operations."""

from datetime import datetime
from pathlib import Path

import pytest

import services.storage_service as storage_service_module
from models.customer import Customer
from services.customer_service import CustomerService
from services.storage_service import StorageService


TIMESTAMP = datetime(2024, 1, 1, 12, 0, 0)


@pytest.fixture
def storage_service(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> StorageService:
    """Provide a StorageService configured with an isolated database."""
    database_path = tmp_path / "database.json"
    monkeypatch.setattr(storage_service_module, "DATABASE_PATH", database_path)
    return StorageService()


@pytest.fixture
def customer_service(storage_service: StorageService) -> CustomerService:
    """Provide a CustomerService backed by temporary storage."""
    return CustomerService(storage_service)


def create_customer(
    customer_id: str = "CUST001",
    first_name: str = "Ada",
    last_name: str = "Lovelace",
    email: str = "ada@example.com",
    phone: str = "555-0100",
    address: str = "1 Computing Lane",
    created_at: datetime = TIMESTAMP,
    updated_at: datetime = TIMESTAMP,
) -> Customer:
    """Create a valid Customer with deterministic timestamps."""
    return Customer(
        id=customer_id,
        first_name=first_name,
        last_name=last_name,
        email=email,
        phone=phone,
        address=address,
        created_at=created_at,
        updated_at=updated_at,
    )


def test_init_accepts_storage_service(storage_service: StorageService) -> None:
    """Accept a valid StorageService dependency."""
    service = CustomerService(storage_service)

    assert service._storage_service is storage_service


def test_init_raises_type_error_for_invalid_storage_service() -> None:
    """Reject a dependency that is not a StorageService."""
    with pytest.raises(TypeError, match="StorageService"):
        CustomerService(object())


def test_add_customer_persists_customer(
    customer_service: CustomerService,
    storage_service: StorageService,
) -> None:
    """Add a customer and persist its serialized data."""
    customer = create_customer()

    customer_service.add_customer(customer)

    assert storage_service.load_data()["customers"] == [customer.to_dict()]


def test_add_customer_raises_type_error_for_non_customer(
    customer_service: CustomerService,
) -> None:
    """Reject a value that is not a Customer."""
    with pytest.raises(TypeError, match="customer must be an instance of Customer"):
        customer_service.add_customer("customer")


def test_add_customer_raises_value_error_for_duplicate_id(
    customer_service: CustomerService,
) -> None:
    """Reject customers that reuse an existing identifier."""
    customer_service.add_customer(create_customer())

    with pytest.raises(ValueError, match="already exists"):
        customer_service.add_customer(create_customer(first_name="Grace"))


def test_get_customer_by_id_returns_matching_customer(
    customer_service: CustomerService,
) -> None:
    """Return the stored Customer matching an identifier."""
    customer = create_customer()
    customer_service.add_customer(customer)

    result = customer_service.get_customer_by_id("CUST001")

    assert result == customer


def test_get_customer_by_id_returns_none_for_missing_customer(
    customer_service: CustomerService,
) -> None:
    """Return None when no customer has the requested identifier."""
    assert customer_service.get_customer_by_id("MISSING") is None


@pytest.mark.parametrize("customer_id", [123, None])
def test_get_customer_by_id_raises_type_error_for_non_string_id(
    customer_service: CustomerService,
    customer_id: object,
) -> None:
    """Reject non-string customer identifiers."""
    with pytest.raises(TypeError, match="customer_id must be a string"):
        customer_service.get_customer_by_id(customer_id)


@pytest.mark.parametrize("customer_id", ["", "   "])
def test_get_customer_by_id_raises_value_error_for_empty_id(
    customer_service: CustomerService,
    customer_id: str,
) -> None:
    """Reject empty customer identifiers after normalization."""
    with pytest.raises(ValueError, match="customer_id cannot be empty"):
        customer_service.get_customer_by_id(customer_id)


def test_get_all_customers_returns_empty_list_for_empty_storage(
    customer_service: CustomerService,
) -> None:
    """Return an empty list when the system has no customers."""
    assert customer_service.get_all_customers() == []


def test_get_all_customers_returns_customers_in_insertion_order(
    customer_service: CustomerService,
) -> None:
    """Return all stored customers as Customer objects in insertion order."""
    first_customer = create_customer()
    second_customer = create_customer(
        customer_id="CUST002",
        first_name="Grace",
        last_name="Hopper",
        email="grace@example.com",
    )
    customer_service.add_customer(first_customer)
    customer_service.add_customer(second_customer)

    customers = customer_service.get_all_customers()

    assert customers == [first_customer, second_customer]
    assert all(isinstance(customer, Customer) for customer in customers)


def test_update_customer_persists_values_and_refreshes_timestamp(
    customer_service: CustomerService,
    storage_service: StorageService,
) -> None:
    """Replace a customer and persist its refreshed update timestamp."""
    customer_service.add_customer(create_customer())
    updated_customer = create_customer(
        first_name="Augusta",
        email="augusta@example.com",
    )
    previous_timestamp = updated_customer.updated_at

    customer_service.update_customer(updated_customer)

    stored_customer = Customer.from_dict(storage_service.load_data()["customers"][0])
    assert stored_customer.first_name == "Augusta"
    assert stored_customer.email == "augusta@example.com"
    assert stored_customer.updated_at > previous_timestamp
    assert stored_customer.updated_at == updated_customer.updated_at


def test_update_customer_raises_type_error_for_invalid_customer(
    customer_service: CustomerService,
) -> None:
    """Reject an update value that is not a Customer."""
    with pytest.raises(TypeError, match="customer must be an instance of Customer"):
        customer_service.update_customer("customer")


def test_update_customer_raises_value_error_for_missing_customer(
    customer_service: CustomerService,
) -> None:
    """Reject an update for a customer that is not stored."""
    with pytest.raises(ValueError, match="does not exist"):
        customer_service.update_customer(create_customer())


def test_delete_customer_removes_customer_from_storage(
    customer_service: CustomerService,
    storage_service: StorageService,
) -> None:
    """Delete an existing customer and persist the removal."""
    customer_service.add_customer(create_customer())

    customer_service.delete_customer("CUST001")

    assert storage_service.load_data()["customers"] == []


@pytest.mark.parametrize("customer_id", [123, None])
def test_delete_customer_raises_type_error_for_non_string_id(
    customer_service: CustomerService,
    customer_id: object,
) -> None:
    """Reject non-string customer identifiers for deletion."""
    with pytest.raises(TypeError, match="customer_id must be a string"):
        customer_service.delete_customer(customer_id)


@pytest.mark.parametrize("customer_id", ["", "   "])
def test_delete_customer_raises_value_error_for_empty_id(
    customer_service: CustomerService,
    customer_id: str,
) -> None:
    """Reject empty customer identifiers for deletion."""
    with pytest.raises(ValueError, match="customer_id cannot be empty"):
        customer_service.delete_customer(customer_id)


def test_delete_customer_raises_value_error_for_missing_customer(
    customer_service: CustomerService,
) -> None:
    """Reject deletion when no customer has the requested identifier."""
    with pytest.raises(ValueError, match="does not exist"):
        customer_service.delete_customer("MISSING")


@pytest.mark.parametrize(
    ("keyword", "customer_id"),
    [
        ("cust001", "CUST001"),
        ("ADA", "CUST001"),
        ("lovelace", "CUST001"),
        ("ADA@EXAMPLE.COM", "CUST001"),
        ("555-0100", "CUST001"),
        ("COMPUTING LANE", "CUST001"),
    ],
)
def test_search_customers_finds_case_insensitive_text_matches(
    customer_service: CustomerService,
    keyword: str,
    customer_id: str,
) -> None:
    """Find customers by identifier, name, email, phone, and address."""
    customer_service.add_customer(create_customer())

    customers = customer_service.search_customers(keyword)

    assert [customer.id for customer in customers] == [customer_id]


def test_search_customers_returns_empty_list_for_no_matches(
    customer_service: CustomerService,
) -> None:
    """Return an empty list when no stored customer matches the keyword."""
    customer_service.add_customer(create_customer())

    assert customer_service.search_customers("missing") == []


def test_search_customers_raises_type_error_for_non_string_keyword(
    customer_service: CustomerService,
) -> None:
    """Reject a keyword that is not a string."""
    with pytest.raises(TypeError, match="keyword must be a string"):
        customer_service.search_customers(123)


@pytest.mark.parametrize("keyword", ["", "   "])
def test_search_customers_raises_value_error_for_empty_keyword(
    customer_service: CustomerService,
    keyword: str,
) -> None:
    """Reject empty keywords after normalization."""
    with pytest.raises(ValueError, match="keyword cannot be empty"):
        customer_service.search_customers(keyword)
