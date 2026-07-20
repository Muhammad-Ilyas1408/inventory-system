"""Unit tests for order-related service operations."""

from datetime import datetime
from pathlib import Path

import pytest

import services.storage_service as storage_service_module
from models.customer import Customer
from models.enums import OrderStatus
from models.order import Order
from models.order_item import OrderItem
from models.product import Product
from services.order_service import OrderService
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
def order_service(storage_service: StorageService) -> OrderService:
    """Provide an OrderService backed by temporary storage."""
    return OrderService(storage_service)


def create_product(
    product_id: str = "PROD001",
    name: str = "Laptop",
    price: float = 1000.0,
    quantity: int = 10,
    created_at: datetime = TIMESTAMP,
    updated_at: datetime = TIMESTAMP,
) -> Product:
    """Create a valid Product with deterministic timestamps."""
    return Product(
        id=product_id,
        name=name,
        category="Electronics",
        price=price,
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
    product_name: str = "Laptop",
    unit_price: float = 1000.0,
    quantity: int = 2,
) -> OrderItem:
    """Create a valid OrderItem for use in test orders."""
    return OrderItem(
        product_id=product_id,
        product_name=product_name,
        unit_price=unit_price,
        quantity=quantity,
    )


def create_order(
    order_id: str = "ORD001",
    customer_id: str = "CUST001",
    items: list[OrderItem] | None = None,
    status: OrderStatus = OrderStatus.PENDING,
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


def seed_database(
    storage_service: StorageService,
    customers: list[Customer] | None = None,
    products: list[Product] | None = None,
) -> None:
    """Persist customer and product dependencies for an order test."""
    data = storage_service.load_data()
    data["customers"] = [customer.to_dict() for customer in customers or []]
    data["products"] = [product.to_dict() for product in products or []]
    storage_service.save_data(data)


def test_init_accepts_storage_service(storage_service: StorageService) -> None:
    """Accept a valid StorageService dependency."""
    service = OrderService(storage_service)

    assert service._storage_service is storage_service


def test_init_raises_type_error_for_invalid_storage_service() -> None:
    """Reject a dependency that is not a StorageService."""
    with pytest.raises(TypeError, match="StorageService"):
        OrderService(object())


def test_create_order_persists_order_and_deducts_inventory(
    order_service: OrderService,
    storage_service: StorageService,
) -> None:
    """Persist an order and deduct inventory with refreshed timestamps."""
    product = create_product()
    order = create_order()
    seed_database(storage_service, [create_customer()], [product])

    order_service.create_order(order)

    data = storage_service.load_data()
    stored_order = Order.from_dict(data["orders"][0])
    stored_product = Product.from_dict(data["products"][0])
    assert stored_order == order
    assert stored_order.updated_at > TIMESTAMP
    assert stored_product.quantity == 8
    assert stored_product.updated_at > TIMESTAMP


def test_create_order_raises_value_error_for_duplicate_id(
    order_service: OrderService,
    storage_service: StorageService,
) -> None:
    """Reject orders that reuse an existing identifier."""
    seed_database(storage_service, [create_customer()], [create_product()])
    order_service.create_order(create_order())

    with pytest.raises(ValueError, match="already exists"):
        order_service.create_order(create_order())


def test_create_order_raises_type_error_for_invalid_order(
    order_service: OrderService,
) -> None:
    """Reject a value that is not an Order."""
    with pytest.raises(TypeError, match="order must be an instance of Order"):
        order_service.create_order("order")


def test_create_order_raises_value_error_for_missing_customer(
    order_service: OrderService,
    storage_service: StorageService,
) -> None:
    """Reject an order that references an unknown customer."""
    seed_database(storage_service, products=[create_product()])

    with pytest.raises(ValueError, match="Customer with ID 'CUST001' does not exist"):
        order_service.create_order(create_order())


def test_create_order_raises_value_error_for_missing_product(
    order_service: OrderService,
    storage_service: StorageService,
) -> None:
    """Reject an order that references an unknown product."""
    seed_database(storage_service, customers=[create_customer()])

    with pytest.raises(ValueError, match="Product with ID 'PROD001' does not exist"):
        order_service.create_order(create_order())


def test_create_order_raises_value_error_for_insufficient_stock(
    order_service: OrderService,
    storage_service: StorageService,
) -> None:
    """Reject an order that exceeds available inventory."""
    seed_database(
        storage_service,
        [create_customer()],
        [create_product(quantity=1)],
    )

    with pytest.raises(ValueError, match="Insufficient stock"):
        order_service.create_order(create_order())


def test_create_order_deducts_multiple_products(
    order_service: OrderService,
    storage_service: StorageService,
) -> None:
    """Deduct the requested quantity for each product in an order."""
    first_product = create_product(quantity=10)
    second_product = create_product(
        product_id="PROD002",
        name="Monitor",
        price=500.0,
        quantity=5,
    )
    order = create_order(
        items=[
            create_order_item(quantity=3),
            create_order_item("PROD002", "Monitor", 500.0, 2),
        ]
    )
    seed_database(storage_service, [create_customer()], [first_product, second_product])

    order_service.create_order(order)

    data = storage_service.load_data()
    assert [product["quantity"] for product in data["products"]] == [7, 3]


def test_create_order_aggregates_duplicate_product_items(
    order_service: OrderService,
    storage_service: StorageService,
) -> None:
    """Validate and deduct the combined quantity for duplicate product items."""
    order = create_order(
        items=[create_order_item(quantity=3), create_order_item(quantity=4)]
    )
    seed_database(storage_service, [create_customer()], [create_product(quantity=6)])

    with pytest.raises(ValueError, match="Insufficient stock"):
        order_service.create_order(order)

    assert storage_service.load_data()["products"][0]["quantity"] == 6


def test_get_order_by_id_returns_matching_order(
    order_service: OrderService,
    storage_service: StorageService,
) -> None:
    """Return the stored Order matching an identifier."""
    order = create_order()
    seed_database(storage_service, [create_customer()], [create_product()])
    order_service.create_order(order)

    result = order_service.get_order_by_id("ORD001")

    assert result == order


def test_get_order_by_id_returns_none_for_missing_order(
    order_service: OrderService,
) -> None:
    """Return None when no order has the requested identifier."""
    assert order_service.get_order_by_id("MISSING") is None


@pytest.mark.parametrize("order_id", [123, None])
def test_get_order_by_id_raises_type_error_for_non_string_id(
    order_service: OrderService,
    order_id: object,
) -> None:
    """Reject non-string order identifiers."""
    with pytest.raises(TypeError, match="order_id must be a string"):
        order_service.get_order_by_id(order_id)


@pytest.mark.parametrize("order_id", ["", "   "])
def test_get_order_by_id_raises_value_error_for_empty_id(
    order_service: OrderService,
    order_id: str,
) -> None:
    """Reject empty order identifiers after normalization."""
    with pytest.raises(ValueError, match="order_id cannot be empty"):
        order_service.get_order_by_id(order_id)


def test_get_all_orders_returns_empty_list_for_empty_storage(
    order_service: OrderService,
) -> None:
    """Return an empty list when the system has no orders."""
    assert order_service.get_all_orders() == []


def test_get_all_orders_returns_orders_in_insertion_order(
    order_service: OrderService,
    storage_service: StorageService,
) -> None:
    """Return all stored orders as Order objects in insertion order."""
    first_order = create_order()
    second_order = create_order(
        order_id="ORD002",
        items=[create_order_item(quantity=1)],
    )
    seed_database(storage_service, [create_customer()], [create_product()])
    order_service.create_order(first_order)
    order_service.create_order(second_order)

    orders = order_service.get_all_orders()

    assert orders == [first_order, second_order]
    assert all(isinstance(order, Order) for order in orders)


def test_update_order_persists_values_and_refreshes_timestamp(
    order_service: OrderService,
    storage_service: StorageService,
) -> None:
    """Replace an order and persist its refreshed update timestamp."""
    order = create_order()
    seed_database(storage_service, [create_customer()], [create_product()])
    order_service.create_order(order)
    updated_order = create_order(status=OrderStatus.COMPLETED)
    previous_timestamp = updated_order.updated_at

    order_service.update_order(updated_order)

    stored_order = Order.from_dict(storage_service.load_data()["orders"][0])
    assert stored_order.status is OrderStatus.COMPLETED
    assert stored_order.updated_at > previous_timestamp
    assert stored_order.updated_at == updated_order.updated_at


def test_update_order_raises_type_error_for_invalid_order(
    order_service: OrderService,
) -> None:
    """Reject an update value that is not an Order."""
    with pytest.raises(TypeError, match="order must be an instance of Order"):
        order_service.update_order("order")


def test_update_order_raises_value_error_for_missing_order(
    order_service: OrderService,
) -> None:
    """Reject an update for an order that is not stored."""
    with pytest.raises(ValueError, match="does not exist"):
        order_service.update_order(create_order())


def test_delete_order_removes_order_and_restores_inventory(
    order_service: OrderService,
    storage_service: StorageService,
) -> None:
    """Delete an order, restore stock, and refresh product timestamps."""
    order = create_order()
    seed_database(storage_service, [create_customer()], [create_product()])
    order_service.create_order(order)
    deducted_timestamp = Product.from_dict(
        storage_service.load_data()["products"][0]
    ).updated_at

    order_service.delete_order("ORD001")

    data = storage_service.load_data()
    restored_product = Product.from_dict(data["products"][0])
    assert data["orders"] == []
    assert restored_product.quantity == 10
    assert restored_product.updated_at > deducted_timestamp


@pytest.mark.parametrize("order_id", [123, None])
def test_delete_order_raises_type_error_for_non_string_id(
    order_service: OrderService,
    order_id: object,
) -> None:
    """Reject non-string order identifiers for deletion."""
    with pytest.raises(TypeError, match="order_id must be a string"):
        order_service.delete_order(order_id)


@pytest.mark.parametrize("order_id", ["", "   "])
def test_delete_order_raises_value_error_for_empty_id(
    order_service: OrderService,
    order_id: str,
) -> None:
    """Reject empty order identifiers for deletion."""
    with pytest.raises(ValueError, match="order_id cannot be empty"):
        order_service.delete_order(order_id)


def test_delete_order_raises_value_error_for_missing_order(
    order_service: OrderService,
) -> None:
    """Reject deletion when no order has the requested identifier."""
    with pytest.raises(ValueError, match="does not exist"):
        order_service.delete_order("MISSING")


@pytest.mark.parametrize(
    "keyword",
    ["ord001", "CUST001", "pending"],
)
def test_search_orders_finds_case_insensitive_matches(
    order_service: OrderService,
    storage_service: StorageService,
    keyword: str,
) -> None:
    """Find orders by identifier, customer identifier, and status."""
    seed_database(storage_service, [create_customer()], [create_product()])
    order_service.create_order(create_order())

    orders = order_service.search_orders(keyword)

    assert [order.id for order in orders] == ["ORD001"]


def test_search_orders_returns_empty_list_for_no_matches(
    order_service: OrderService,
    storage_service: StorageService,
) -> None:
    """Return an empty list when no stored order matches the keyword."""
    seed_database(storage_service, [create_customer()], [create_product()])
    order_service.create_order(create_order())

    assert order_service.search_orders("missing") == []


def test_search_orders_raises_type_error_for_non_string_keyword(
    order_service: OrderService,
) -> None:
    """Reject a keyword that is not a string."""
    with pytest.raises(TypeError, match="keyword must be a string"):
        order_service.search_orders(123)


@pytest.mark.parametrize("keyword", ["", "   "])
def test_search_orders_raises_value_error_for_empty_keyword(
    order_service: OrderService,
    keyword: str,
) -> None:
    """Reject empty keywords after normalization."""
    with pytest.raises(ValueError, match="keyword cannot be empty"):
        order_service.search_orders(keyword)


def test_get_orders_by_customer_returns_one_order(
    order_service: OrderService,
    storage_service: StorageService,
) -> None:
    """Return the order associated with a customer identifier."""
    order = create_order()
    seed_database(storage_service, [create_customer()], [create_product()])
    order_service.create_order(order)

    orders = order_service.get_orders_by_customer("CUST001")

    assert orders == [order]


def test_get_orders_by_customer_returns_multiple_orders(
    order_service: OrderService,
    storage_service: StorageService,
) -> None:
    """Return every order associated with a customer identifier."""
    first_order = create_order()
    second_order = create_order(
        order_id="ORD002",
        items=[create_order_item(quantity=1)],
    )
    seed_database(storage_service, [create_customer()], [create_product()])
    order_service.create_order(first_order)
    order_service.create_order(second_order)

    orders = order_service.get_orders_by_customer("CUST001")

    assert orders == [first_order, second_order]


def test_get_orders_by_customer_returns_empty_list_for_no_orders(
    order_service: OrderService,
) -> None:
    """Return an empty list when a customer has no orders."""
    assert order_service.get_orders_by_customer("CUST001") == []


@pytest.mark.parametrize("customer_id", [123, None])
def test_get_orders_by_customer_raises_type_error_for_non_string_id(
    order_service: OrderService,
    customer_id: object,
) -> None:
    """Reject non-string customer identifiers."""
    with pytest.raises(TypeError, match="customer_id must be a string"):
        order_service.get_orders_by_customer(customer_id)


@pytest.mark.parametrize("customer_id", ["", "   "])
def test_get_orders_by_customer_raises_value_error_for_empty_id(
    order_service: OrderService,
    customer_id: str,
) -> None:
    """Reject empty customer identifiers after normalization."""
    with pytest.raises(ValueError, match="customer_id cannot be empty"):
        order_service.get_orders_by_customer(customer_id)


@pytest.mark.parametrize(
    ("items", "expected_total"),
    [
        ([create_order_item(quantity=2)], 2000.0),
        (
            [
                create_order_item(quantity=2),
                create_order_item("PROD002", "Monitor", 500.0, 3),
            ],
            3500.0,
        ),
    ],
)
def test_calculate_order_total_returns_item_subtotals(
    order_service: OrderService,
    storage_service: StorageService,
    items: list[OrderItem],
    expected_total: float,
) -> None:
    """Return the total of single-item and multi-item orders."""
    products = [create_product()]
    if len(items) > 1:
        products.append(
            create_product(
                product_id="PROD002",
                name="Monitor",
                price=500.0,
            )
        )
    seed_database(storage_service, [create_customer()], products)
    order_service.create_order(create_order(items=items))

    total = order_service.calculate_order_total("ORD001")

    assert total == expected_total


def test_calculate_order_total_raises_value_error_for_missing_order(
    order_service: OrderService,
) -> None:
    """Reject total calculations for orders that are not stored."""
    with pytest.raises(ValueError, match="does not exist"):
        order_service.calculate_order_total("MISSING")


@pytest.mark.parametrize("order_id", [123, None])
def test_calculate_order_total_raises_type_error_for_non_string_id(
    order_service: OrderService,
    order_id: object,
) -> None:
    """Reject non-string order identifiers for total calculations."""
    with pytest.raises(TypeError, match="order_id must be a string"):
        order_service.calculate_order_total(order_id)


@pytest.mark.parametrize("order_id", ["", "   "])
def test_calculate_order_total_raises_value_error_for_empty_id(
    order_service: OrderService,
    order_id: str,
) -> None:
    """Reject empty order identifiers for total calculations."""
    with pytest.raises(ValueError, match="order_id cannot be empty"):
        order_service.calculate_order_total(order_id)
