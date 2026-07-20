"""Unit tests for invoice-related service operations."""

from datetime import datetime
from pathlib import Path

import pytest

import services.storage_service as storage_service_module
from models.customer import Customer
from models.enums import OrderStatus
from models.invoice import Invoice
from models.order import Order
from models.order_item import OrderItem
from models.product import Product
from services.invoice_service import InvoiceService
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
def invoice_service(storage_service: StorageService) -> InvoiceService:
    """Provide an InvoiceService backed by temporary storage."""
    return InvoiceService(storage_service)


def create_product(
    product_id: str = "PROD001",
    created_at: datetime = TIMESTAMP,
    updated_at: datetime = TIMESTAMP,
) -> Product:
    """Create a valid Product with deterministic timestamps."""
    return Product(
        id=product_id,
        name="Laptop",
        category="Electronics",
        price=1000.0,
        quantity=10,
        supplier="Acme Supplies",
        created_at=created_at,
        updated_at=updated_at,
    )


def create_customer(
    customer_id: str = "CUST001",
    created_at: datetime = TIMESTAMP,
    updated_at: datetime = TIMESTAMP,
) -> Customer:
    """Create a valid Customer with deterministic timestamps."""
    return Customer(
        id=customer_id,
        first_name="Ada",
        last_name="Lovelace",
        email="ada@example.com",
        phone="555-0100",
        address="1 Computing Lane",
        created_at=created_at,
        updated_at=updated_at,
    )


def create_order_item(
    product_id: str = "PROD001",
    quantity: int = 2,
) -> OrderItem:
    """Create a valid OrderItem for use in test records."""
    return OrderItem(
        product_id=product_id,
        product_name="Laptop",
        unit_price=1000.0,
        quantity=quantity,
    )


def create_order(
    order_id: str = "ORD001",
    customer_id: str = "CUST001",
    status: OrderStatus = OrderStatus.PENDING,
    items: list[OrderItem] | None = None,
    created_at: datetime = TIMESTAMP,
    updated_at: datetime = TIMESTAMP,
) -> Order:
    """Create a valid Order with deterministic timestamps."""
    return Order(
        id=order_id,
        customer_id=customer_id,
        items=items or [create_order_item()],
        status=status,
        created_at=created_at,
        updated_at=updated_at,
    )


def create_invoice(
    invoice_id: str = "INV001",
    order_id: str = "ORD001",
    customer_name: str = "Ada Lovelace",
    customer_email: str = "ada@example.com",
    items: list[OrderItem] | None = None,
    subtotal: float = 2000.0,
    total: float = 2000.0,
    issued_at: datetime = TIMESTAMP,
) -> Invoice:
    """Create a valid Invoice with a deterministic issue timestamp."""
    return Invoice(
        id=invoice_id,
        order_id=order_id,
        customer_name=customer_name,
        customer_email=customer_email,
        items=items or [create_order_item()],
        subtotal=subtotal,
        total=total,
        issued_at=issued_at,
    )


def seed_database(
    storage_service: StorageService,
    customers: list[Customer] | None = None,
    products: list[Product] | None = None,
    orders: list[Order] | None = None,
) -> None:
    """Persist dependency records needed for invoice tests."""
    data = storage_service.load_data()
    data["customers"] = [customer.to_dict() for customer in customers or []]
    data["products"] = [product.to_dict() for product in products or []]
    data["orders"] = [order.to_dict() for order in orders or []]
    storage_service.save_data(data)


def test_init_accepts_storage_service(storage_service: StorageService) -> None:
    """Accept a valid StorageService dependency."""
    service = InvoiceService(storage_service)

    assert service._storage_service is storage_service


def test_init_raises_type_error_for_invalid_storage_service() -> None:
    """Reject a dependency that is not a StorageService."""
    with pytest.raises(TypeError, match="StorageService"):
        InvoiceService(object())


def test_create_invoice_persists_serialized_invoice(
    invoice_service: InvoiceService,
    storage_service: StorageService,
) -> None:
    """Persist an invoice that references an existing order."""
    invoice = create_invoice()
    seed_database(
        storage_service,
        [create_customer()],
        [create_product()],
        [create_order()],
    )

    invoice_service.create_invoice(invoice)

    stored_data = storage_service.load_data()["invoices"]
    assert stored_data == [invoice.to_dict()]
    assert Invoice.from_dict(stored_data[0]) == invoice


def test_create_invoice_raises_value_error_for_duplicate_id(
    invoice_service: InvoiceService,
    storage_service: StorageService,
) -> None:
    """Reject invoices that reuse an existing identifier."""
    seed_database(storage_service, orders=[create_order()])
    invoice_service.create_invoice(create_invoice())

    with pytest.raises(ValueError, match="already exists"):
        invoice_service.create_invoice(create_invoice())


def test_create_invoice_raises_type_error_for_invalid_invoice(
    invoice_service: InvoiceService,
) -> None:
    """Reject a value that is not an Invoice."""
    with pytest.raises(TypeError, match="invoice must be an instance of Invoice"):
        invoice_service.create_invoice("invoice")


def test_create_invoice_raises_value_error_for_missing_order(
    invoice_service: InvoiceService,
) -> None:
    """Reject an invoice that references an unknown order."""
    with pytest.raises(ValueError, match="Order with ID 'ORD001' does not exist"):
        invoice_service.create_invoice(create_invoice())


def test_get_invoice_by_id_returns_matching_invoice(
    invoice_service: InvoiceService,
    storage_service: StorageService,
) -> None:
    """Return the stored Invoice matching an identifier."""
    invoice = create_invoice()
    seed_database(storage_service, orders=[create_order()])
    invoice_service.create_invoice(invoice)

    result = invoice_service.get_invoice_by_id("INV001")

    assert result == invoice
    assert isinstance(result, Invoice)


def test_get_invoice_by_id_returns_none_for_missing_invoice(
    invoice_service: InvoiceService,
) -> None:
    """Return None when no invoice has the requested identifier."""
    assert invoice_service.get_invoice_by_id("MISSING") is None


@pytest.mark.parametrize("invoice_id", [123, None])
def test_get_invoice_by_id_raises_type_error_for_non_string_id(
    invoice_service: InvoiceService,
    invoice_id: object,
) -> None:
    """Reject non-string invoice identifiers."""
    with pytest.raises(TypeError, match="invoice_id must be a string"):
        invoice_service.get_invoice_by_id(invoice_id)


@pytest.mark.parametrize("invoice_id", ["", "   "])
def test_get_invoice_by_id_raises_value_error_for_empty_id(
    invoice_service: InvoiceService,
    invoice_id: str,
) -> None:
    """Reject empty invoice identifiers after normalization."""
    with pytest.raises(ValueError, match="invoice_id cannot be empty"):
        invoice_service.get_invoice_by_id(invoice_id)


def test_get_all_invoices_returns_empty_list_for_empty_storage(
    invoice_service: InvoiceService,
) -> None:
    """Return an empty list when the system has no invoices."""
    assert invoice_service.get_all_invoices() == []


def test_get_all_invoices_returns_single_invoice(
    invoice_service: InvoiceService,
    storage_service: StorageService,
) -> None:
    """Return a single stored invoice as an Invoice object."""
    invoice = create_invoice()
    seed_database(storage_service, orders=[create_order()])
    invoice_service.create_invoice(invoice)

    invoices = invoice_service.get_all_invoices()

    assert invoices == [invoice]
    assert isinstance(invoices[0], Invoice)


def test_get_all_invoices_preserves_insertion_order(
    invoice_service: InvoiceService,
    storage_service: StorageService,
) -> None:
    """Return multiple invoices in their stored insertion order."""
    first_invoice = create_invoice()
    second_invoice = create_invoice(invoice_id="INV002", order_id="ORD002")
    seed_database(
        storage_service,
        orders=[create_order(), create_order(order_id="ORD002")],
    )
    invoice_service.create_invoice(first_invoice)
    invoice_service.create_invoice(second_invoice)

    invoices = invoice_service.get_all_invoices()

    assert invoices == [first_invoice, second_invoice]


def test_update_invoice_persists_updated_data(
    invoice_service: InvoiceService,
    storage_service: StorageService,
) -> None:
    """Replace a stored invoice with its updated data."""
    invoice = create_invoice()
    updated_invoice = create_invoice(
        customer_name="Augusta Ada King",
        customer_email="augusta@example.com",
        total=2200.0,
    )
    seed_database(storage_service, orders=[create_order()])
    invoice_service.create_invoice(invoice)

    invoice_service.update_invoice(updated_invoice)

    stored_invoice = Invoice.from_dict(storage_service.load_data()["invoices"][0])
    assert stored_invoice.customer_name == "Augusta Ada King"
    assert stored_invoice.customer_email == "augusta@example.com"
    assert stored_invoice.total == 2200.0


def test_update_invoice_raises_type_error_for_invalid_invoice(
    invoice_service: InvoiceService,
) -> None:
    """Reject an update value that is not an Invoice."""
    with pytest.raises(TypeError, match="invoice must be an instance of Invoice"):
        invoice_service.update_invoice("invoice")


def test_update_invoice_raises_value_error_for_missing_invoice(
    invoice_service: InvoiceService,
) -> None:
    """Reject an update for an invoice that is not stored."""
    with pytest.raises(ValueError, match="does not exist"):
        invoice_service.update_invoice(create_invoice())


def test_delete_invoice_removes_invoice_from_storage(
    invoice_service: InvoiceService,
    storage_service: StorageService,
) -> None:
    """Delete an existing invoice and persist the removal."""
    seed_database(storage_service, orders=[create_order()])
    invoice_service.create_invoice(create_invoice())

    invoice_service.delete_invoice("INV001")

    assert storage_service.load_data()["invoices"] == []


@pytest.mark.parametrize("invoice_id", [123, None])
def test_delete_invoice_raises_type_error_for_non_string_id(
    invoice_service: InvoiceService,
    invoice_id: object,
) -> None:
    """Reject non-string invoice identifiers for deletion."""
    with pytest.raises(TypeError, match="invoice_id must be a string"):
        invoice_service.delete_invoice(invoice_id)


@pytest.mark.parametrize("invoice_id", ["", "   "])
def test_delete_invoice_raises_value_error_for_empty_id(
    invoice_service: InvoiceService,
    invoice_id: str,
) -> None:
    """Reject empty invoice identifiers for deletion."""
    with pytest.raises(ValueError, match="invoice_id cannot be empty"):
        invoice_service.delete_invoice(invoice_id)


def test_delete_invoice_raises_value_error_for_missing_invoice(
    invoice_service: InvoiceService,
) -> None:
    """Reject deletion when no invoice has the requested identifier."""
    with pytest.raises(ValueError, match="does not exist"):
        invoice_service.delete_invoice("MISSING")


@pytest.mark.parametrize(
    "keyword",
    ["inv001", "ORD001", "cust001", "pending"],
)
def test_search_invoices_finds_case_insensitive_matches(
    invoice_service: InvoiceService,
    storage_service: StorageService,
    keyword: str,
) -> None:
    """Find invoices by invoice, order, customer, and order status values."""
    seed_database(
        storage_service,
        orders=[create_order(status=OrderStatus.PENDING)],
    )
    invoice_service.create_invoice(create_invoice())

    invoices = invoice_service.search_invoices(keyword)

    assert [invoice.id for invoice in invoices] == ["INV001"]


def test_search_invoices_returns_empty_list_for_no_matches(
    invoice_service: InvoiceService,
    storage_service: StorageService,
) -> None:
    """Return an empty list when no stored invoice matches the keyword."""
    seed_database(storage_service, orders=[create_order()])
    invoice_service.create_invoice(create_invoice())

    assert invoice_service.search_invoices("missing") == []


def test_search_invoices_raises_type_error_for_non_string_keyword(
    invoice_service: InvoiceService,
) -> None:
    """Reject a keyword that is not a string."""
    with pytest.raises(TypeError, match="keyword must be a string"):
        invoice_service.search_invoices(123)


@pytest.mark.parametrize("keyword", ["", "   "])
def test_search_invoices_raises_value_error_for_empty_keyword(
    invoice_service: InvoiceService,
    keyword: str,
) -> None:
    """Reject empty keywords after normalization."""
    with pytest.raises(ValueError, match="keyword cannot be empty"):
        invoice_service.search_invoices(keyword)


def test_get_invoices_by_customer_returns_one_invoice(
    invoice_service: InvoiceService,
    storage_service: StorageService,
) -> None:
    """Return the invoice associated with a customer's order."""
    invoice = create_invoice()
    seed_database(storage_service, orders=[create_order()])
    invoice_service.create_invoice(invoice)

    invoices = invoice_service.get_invoices_by_customer("CUST001")

    assert invoices == [invoice]


def test_get_invoices_by_customer_returns_multiple_invoices(
    invoice_service: InvoiceService,
    storage_service: StorageService,
) -> None:
    """Return every invoice associated with a customer's orders."""
    first_invoice = create_invoice()
    second_invoice = create_invoice(invoice_id="INV002", order_id="ORD002")
    seed_database(
        storage_service,
        orders=[create_order(), create_order(order_id="ORD002")],
    )
    invoice_service.create_invoice(first_invoice)
    invoice_service.create_invoice(second_invoice)

    invoices = invoice_service.get_invoices_by_customer("CUST001")

    assert invoices == [first_invoice, second_invoice]


def test_get_invoices_by_customer_returns_empty_list_for_no_invoices(
    invoice_service: InvoiceService,
) -> None:
    """Return an empty list when a customer has no invoices."""
    assert invoice_service.get_invoices_by_customer("CUST001") == []


@pytest.mark.parametrize("customer_id", [123, None])
def test_get_invoices_by_customer_raises_type_error_for_non_string_id(
    invoice_service: InvoiceService,
    customer_id: object,
) -> None:
    """Reject non-string customer identifiers."""
    with pytest.raises(TypeError, match="customer_id must be a string"):
        invoice_service.get_invoices_by_customer(customer_id)


@pytest.mark.parametrize("customer_id", ["", "   "])
def test_get_invoices_by_customer_raises_value_error_for_empty_id(
    invoice_service: InvoiceService,
    customer_id: str,
) -> None:
    """Reject empty customer identifiers after normalization."""
    with pytest.raises(ValueError, match="customer_id cannot be empty"):
        invoice_service.get_invoices_by_customer(customer_id)


def test_get_invoice_by_order_returns_matching_invoice(
    invoice_service: InvoiceService,
    storage_service: StorageService,
) -> None:
    """Return the invoice that references a stored order."""
    invoice = create_invoice()
    seed_database(storage_service, orders=[create_order()])
    invoice_service.create_invoice(invoice)

    result = invoice_service.get_invoice_by_order("ORD001")

    assert result == invoice
    assert isinstance(result, Invoice)


def test_get_invoice_by_order_returns_none_for_missing_order(
    invoice_service: InvoiceService,
) -> None:
    """Return None when no invoice references the requested order."""
    assert invoice_service.get_invoice_by_order("MISSING") is None


@pytest.mark.parametrize("order_id", [123, None])
def test_get_invoice_by_order_raises_type_error_for_non_string_id(
    invoice_service: InvoiceService,
    order_id: object,
) -> None:
    """Reject non-string order identifiers for invoice lookups."""
    with pytest.raises(TypeError, match="order_id must be a string"):
        invoice_service.get_invoice_by_order(order_id)


@pytest.mark.parametrize("order_id", ["", "   "])
def test_get_invoice_by_order_raises_value_error_for_empty_id(
    invoice_service: InvoiceService,
    order_id: str,
) -> None:
    """Reject empty order identifiers for invoice lookups."""
    with pytest.raises(ValueError, match="order_id cannot be empty"):
        invoice_service.get_invoice_by_order(order_id)
