"""Unit tests for read-only report service operations."""

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
from services.report_service import ReportService
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
def report_service(storage_service: StorageService) -> ReportService:
    """Provide a ReportService backed by temporary storage."""
    return ReportService(storage_service)


def create_product(
    product_id: str = "PROD001",
    quantity: int = 10,
    created_at: datetime = TIMESTAMP,
    updated_at: datetime = TIMESTAMP,
) -> Product:
    """Create a valid Product with deterministic timestamps."""
    return Product(
        id=product_id,
        name="Laptop",
        category="Electronics",
        price=1000.0,
        quantity=quantity,
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
    items: list[OrderItem] | None = None,
    created_at: datetime = TIMESTAMP,
    updated_at: datetime = TIMESTAMP,
) -> Order:
    """Create a valid Order with deterministic timestamps."""
    return Order(
        id=order_id,
        customer_id=customer_id,
        items=items or [create_order_item()],
        status=OrderStatus.PENDING,
        created_at=created_at,
        updated_at=updated_at,
    )


def create_invoice(
    invoice_id: str = "INV001",
    order_id: str = "ORD001",
    total: float = 2000.0,
    issued_at: datetime = TIMESTAMP,
) -> Invoice:
    """Create a valid Invoice with a deterministic issue timestamp."""
    return Invoice(
        id=invoice_id,
        order_id=order_id,
        customer_name="Ada Lovelace",
        customer_email="ada@example.com",
        items=[create_order_item()],
        subtotal=total,
        total=total,
        issued_at=issued_at,
    )


def seed_database(
    storage_service: StorageService,
    customers: list[Customer] | None = None,
    products: list[Product] | None = None,
    orders: list[Order] | None = None,
    invoices: list[Invoice] | None = None,
) -> None:
    """Persist records required for a report test."""
    data = storage_service.load_data()
    data["customers"] = [customer.to_dict() for customer in customers or []]
    data["products"] = [product.to_dict() for product in products or []]
    data["orders"] = [order.to_dict() for order in orders or []]
    data["invoices"] = [invoice.to_dict() for invoice in invoices or []]
    storage_service.save_data(data)


def test_init_accepts_storage_service(storage_service: StorageService) -> None:
    """Accept a valid StorageService dependency."""
    service = ReportService(storage_service)

    assert service._storage_service is storage_service


def test_init_raises_type_error_for_invalid_storage_service() -> None:
    """Reject a dependency that is not a StorageService."""
    with pytest.raises(TypeError, match="StorageService"):
        ReportService(object())


def test_get_inventory_summary_returns_empty_database_totals(
    report_service: ReportService,
) -> None:
    """Return zero inventory counts for an empty database."""
    assert report_service.get_inventory_summary() == {
        "total_products": 0,
        "total_stock": 0,
    }


def test_get_inventory_summary_returns_one_product_totals(
    report_service: ReportService,
    storage_service: StorageService,
) -> None:
    """Return accurate counts for one stored product."""
    seed_database(storage_service, products=[create_product(quantity=7)])

    assert report_service.get_inventory_summary() == {
        "total_products": 1,
        "total_stock": 7,
    }


def test_get_inventory_summary_returns_multiple_product_totals(
    report_service: ReportService,
    storage_service: StorageService,
) -> None:
    """Return accurate counts and stock for multiple products."""
    seed_database(
        storage_service,
        products=[
            create_product(quantity=7),
            create_product(product_id="PROD002", quantity=3),
        ],
    )

    assert report_service.get_inventory_summary() == {
        "total_products": 2,
        "total_stock": 10,
    }


def test_get_low_stock_products_uses_default_threshold(
    report_service: ReportService,
    storage_service: StorageService,
) -> None:
    """Return products at or below the default low-stock threshold."""
    low_stock_product = create_product(quantity=5)
    seed_database(
        storage_service,
        products=[low_stock_product, create_product(product_id="PROD002", quantity=6)],
    )

    products = report_service.get_low_stock_products()

    assert products == [low_stock_product]
    assert isinstance(products[0], Product)


def test_get_low_stock_products_uses_custom_threshold(
    report_service: ReportService,
    storage_service: StorageService,
) -> None:
    """Return products at or below a custom low-stock threshold."""
    second_product = create_product(product_id="PROD002", quantity=3)
    seed_database(
        storage_service,
        products=[create_product(quantity=2), second_product],
    )

    assert report_service.get_low_stock_products(3) == [
        create_product(quantity=2),
        second_product,
    ]


def test_get_low_stock_products_supports_zero_threshold(
    report_service: ReportService,
    storage_service: StorageService,
) -> None:
    """Return out-of-stock products when the threshold is zero."""
    out_of_stock_product = create_product(quantity=0)
    seed_database(
        storage_service,
        products=[
            out_of_stock_product,
            create_product(product_id="PROD002", quantity=1),
        ],
    )

    assert report_service.get_low_stock_products(0) == [out_of_stock_product]


def test_get_low_stock_products_returns_empty_list_when_none_match(
    report_service: ReportService,
    storage_service: StorageService,
) -> None:
    """Return an empty list when no products meet the threshold."""
    seed_database(storage_service, products=[create_product(quantity=6)])

    assert report_service.get_low_stock_products() == []


def test_get_low_stock_products_returns_all_matching_products(
    report_service: ReportService,
    storage_service: StorageService,
) -> None:
    """Preserve storage order when every product meets the threshold."""
    first_product = create_product(quantity=2)
    second_product = create_product(product_id="PROD002", quantity=4)
    seed_database(storage_service, products=[first_product, second_product])

    assert report_service.get_low_stock_products() == [first_product, second_product]


@pytest.mark.parametrize("threshold", ["5", 5.0, None])
def test_get_low_stock_products_raises_type_error_for_non_integer_threshold(
    report_service: ReportService,
    threshold: object,
) -> None:
    """Reject low-stock thresholds that are not integers."""
    with pytest.raises(TypeError, match="threshold must be an integer"):
        report_service.get_low_stock_products(threshold)


def test_get_low_stock_products_raises_type_error_for_boolean_threshold(
    report_service: ReportService,
) -> None:
    """Reject boolean values for the low-stock threshold."""
    with pytest.raises(TypeError, match="threshold must be an integer"):
        report_service.get_low_stock_products(True)


def test_get_low_stock_products_raises_value_error_for_negative_threshold(
    report_service: ReportService,
) -> None:
    """Reject negative low-stock thresholds."""
    with pytest.raises(ValueError, match="greater than or equal to 0"):
        report_service.get_low_stock_products(-1)


def test_get_total_sales_returns_zero_for_no_invoices(
    report_service: ReportService,
) -> None:
    """Return zero sales when no invoices are stored."""
    assert report_service.get_total_sales() == 0.0


def test_get_total_sales_returns_one_invoice_total(
    report_service: ReportService,
    storage_service: StorageService,
) -> None:
    """Return the total from one stored invoice."""
    seed_database(storage_service, invoices=[create_invoice(total=1250.5)])

    assert report_service.get_total_sales() == 1250.5


def test_get_total_sales_returns_multiple_invoice_totals(
    report_service: ReportService,
    storage_service: StorageService,
) -> None:
    """Return the sum of all stored invoice totals."""
    seed_database(
        storage_service,
        invoices=[
            create_invoice(total=1250.5),
            create_invoice(invoice_id="INV002", order_id="ORD002", total=749.5),
        ],
    )

    assert report_service.get_total_sales() == 2000.0


@pytest.mark.parametrize(
    ("orders", "expected_count"),
    [([], 0), ([create_order()], 1), ([create_order(), create_order("ORD002")], 2)],
)
def test_get_total_orders_returns_stored_order_count(
    report_service: ReportService,
    storage_service: StorageService,
    orders: list[Order],
    expected_count: int,
) -> None:
    """Return the total number of stored orders."""
    seed_database(storage_service, orders=orders)

    assert report_service.get_total_orders() == expected_count


@pytest.mark.parametrize(
    ("customers", "expected_count"),
    [
        ([], 0),
        ([create_customer()], 1),
        ([create_customer(), create_customer("CUST002")], 2),
    ],
)
def test_get_total_customers_returns_stored_customer_count(
    report_service: ReportService,
    storage_service: StorageService,
    customers: list[Customer],
    expected_count: int,
) -> None:
    """Return the total number of stored customers."""
    seed_database(storage_service, customers=customers)

    assert report_service.get_total_customers() == expected_count


@pytest.mark.parametrize(
    ("invoices", "expected_count"),
    [
        ([], 0),
        ([create_invoice()], 1),
        (
            [
                create_invoice(),
                create_invoice(invoice_id="INV002", order_id="ORD002"),
            ],
            2,
        ),
    ],
)
def test_get_total_invoices_returns_stored_invoice_count(
    report_service: ReportService,
    storage_service: StorageService,
    invoices: list[Invoice],
    expected_count: int,
) -> None:
    """Return the total number of stored invoices."""
    seed_database(storage_service, invoices=invoices)

    assert report_service.get_total_invoices() == expected_count
