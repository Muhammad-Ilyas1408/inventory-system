"""Unit tests for product-related inventory operations."""

from datetime import datetime
from pathlib import Path

import pytest

import services.storage_service as storage_service_module
from models.product import Product
from services.inventory_service import InventoryService
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
def inventory_service(storage_service: StorageService) -> InventoryService:
    """Provide an InventoryService backed by temporary storage."""
    return InventoryService(storage_service)


def create_product(
    product_id: str = "PROD001",
    name: str = "Laptop",
    category: str = "Electronics",
    price: float = 1000.0,
    quantity: int = 10,
    supplier: str = "Acme Supplies",
    created_at: datetime = TIMESTAMP,
    updated_at: datetime = TIMESTAMP,
) -> Product:
    """Create a valid Product with deterministic timestamps."""
    return Product(
        id=product_id,
        name=name,
        category=category,
        price=price,
        quantity=quantity,
        supplier=supplier,
        created_at=created_at,
        updated_at=updated_at,
    )


def test_init_accepts_storage_service(storage_service: StorageService) -> None:
    """Accept a valid StorageService dependency."""
    service = InventoryService(storage_service)

    assert service._storage_service is storage_service


def test_init_raises_type_error_for_invalid_storage_service() -> None:
    """Reject a dependency that is not a StorageService."""
    with pytest.raises(TypeError, match="StorageService"):
        InventoryService(object())


def test_add_product_persists_product(
    inventory_service: InventoryService,
    storage_service: StorageService,
) -> None:
    """Add a product and persist its serialized data."""
    product = create_product()

    inventory_service.add_product(product)

    assert storage_service.load_data()["products"] == [product.to_dict()]


def test_add_product_raises_type_error_for_non_product(
    inventory_service: InventoryService,
) -> None:
    """Reject a value that is not a Product."""
    with pytest.raises(TypeError, match="product must be an instance of Product"):
        inventory_service.add_product("product")


def test_add_product_raises_value_error_for_duplicate_id(
    inventory_service: InventoryService,
) -> None:
    """Reject products that reuse an existing identifier."""
    inventory_service.add_product(create_product())

    with pytest.raises(ValueError, match="already exists"):
        inventory_service.add_product(create_product(name="Updated Laptop"))


def test_get_product_by_id_returns_matching_product(
    inventory_service: InventoryService,
) -> None:
    """Return the stored Product matching an identifier."""
    product = create_product()
    inventory_service.add_product(product)

    result = inventory_service.get_product_by_id("PROD001")

    assert result == product


def test_get_product_by_id_returns_none_for_missing_product(
    inventory_service: InventoryService,
) -> None:
    """Return None when no product has the requested identifier."""
    assert inventory_service.get_product_by_id("MISSING") is None


@pytest.mark.parametrize("product_id", [123, None])
def test_get_product_by_id_raises_type_error_for_non_string_id(
    inventory_service: InventoryService,
    product_id: object,
) -> None:
    """Reject non-string product identifiers."""
    with pytest.raises(TypeError, match="product_id must be a string"):
        inventory_service.get_product_by_id(product_id)


@pytest.mark.parametrize("product_id", ["", "   "])
def test_get_product_by_id_raises_value_error_for_empty_id(
    inventory_service: InventoryService,
    product_id: str,
) -> None:
    """Reject empty product identifiers after normalization."""
    with pytest.raises(ValueError, match="product_id cannot be empty"):
        inventory_service.get_product_by_id(product_id)


def test_get_all_products_returns_empty_list_for_empty_inventory(
    inventory_service: InventoryService,
) -> None:
    """Return an empty list when the inventory has no products."""
    assert inventory_service.get_all_products() == []


def test_get_all_products_returns_product_instances(
    inventory_service: InventoryService,
) -> None:
    """Return all stored products as Product objects in storage order."""
    first_product = create_product()
    second_product = create_product(product_id="PROD002", name="Monitor")
    inventory_service.add_product(first_product)
    inventory_service.add_product(second_product)

    products = inventory_service.get_all_products()

    assert products == [first_product, second_product]
    assert all(isinstance(product, Product) for product in products)


def test_update_product_persists_values_and_refreshes_timestamp(
    inventory_service: InventoryService,
    storage_service: StorageService,
) -> None:
    """Replace a product and persist its refreshed update timestamp."""
    inventory_service.add_product(create_product())
    updated_product = create_product(name="Updated Laptop", price=1200.0)
    previous_timestamp = updated_product.updated_at

    inventory_service.update_product(updated_product)

    stored_product = Product.from_dict(storage_service.load_data()["products"][0])
    assert stored_product.name == "Updated Laptop"
    assert stored_product.price == 1200.0
    assert stored_product.updated_at > previous_timestamp
    assert stored_product.updated_at == updated_product.updated_at


def test_update_product_raises_type_error_for_invalid_product(
    inventory_service: InventoryService,
) -> None:
    """Reject an update value that is not a Product."""
    with pytest.raises(TypeError, match="product must be an instance of Product"):
        inventory_service.update_product("product")


def test_update_product_raises_value_error_for_missing_product(
    inventory_service: InventoryService,
) -> None:
    """Reject an update for a product that is not stored."""
    with pytest.raises(ValueError, match="does not exist"):
        inventory_service.update_product(create_product())


def test_delete_product_removes_product_from_storage(
    inventory_service: InventoryService,
    storage_service: StorageService,
) -> None:
    """Delete an existing product and persist the removal."""
    inventory_service.add_product(create_product())

    inventory_service.delete_product("PROD001")

    assert storage_service.load_data()["products"] == []


@pytest.mark.parametrize("product_id", [123, None])
def test_delete_product_raises_type_error_for_non_string_id(
    inventory_service: InventoryService,
    product_id: object,
) -> None:
    """Reject non-string product identifiers for deletion."""
    with pytest.raises(TypeError, match="product_id must be a string"):
        inventory_service.delete_product(product_id)


@pytest.mark.parametrize("product_id", ["", "   "])
def test_delete_product_raises_value_error_for_empty_id(
    inventory_service: InventoryService,
    product_id: str,
) -> None:
    """Reject empty product identifiers for deletion."""
    with pytest.raises(ValueError, match="product_id cannot be empty"):
        inventory_service.delete_product(product_id)


def test_delete_product_raises_value_error_for_missing_product(
    inventory_service: InventoryService,
) -> None:
    """Reject deletion when no product has the requested identifier."""
    with pytest.raises(ValueError, match="does not exist"):
        inventory_service.delete_product("MISSING")


@pytest.mark.parametrize(
    ("keyword", "product_id"),
    [
        ("prod001", "PROD001"),
        ("LAPTOP", "PROD001"),
        ("electronics", "PROD001"),
        ("ACME SUPPLIES", "PROD001"),
    ],
)
def test_search_products_finds_case_insensitive_text_matches(
    inventory_service: InventoryService,
    keyword: str,
    product_id: str,
) -> None:
    """Find products by identifier, name, category, and supplier."""
    inventory_service.add_product(create_product(name="Laptop Pro"))

    products = inventory_service.search_products(keyword)

    assert [product.id for product in products] == [product_id]


def test_search_products_returns_empty_list_for_no_matches(
    inventory_service: InventoryService,
) -> None:
    """Return an empty list when no stored product matches the keyword."""
    inventory_service.add_product(create_product())

    assert inventory_service.search_products("camera") == []


def test_search_products_raises_type_error_for_non_string_keyword(
    inventory_service: InventoryService,
) -> None:
    """Reject a keyword that is not a string."""
    with pytest.raises(TypeError, match="keyword must be a string"):
        inventory_service.search_products(123)


@pytest.mark.parametrize("keyword", ["", "   "])
def test_search_products_raises_value_error_for_empty_keyword(
    inventory_service: InventoryService,
    keyword: str,
) -> None:
    """Reject empty keywords after normalization."""
    with pytest.raises(ValueError, match="keyword cannot be empty"):
        inventory_service.search_products(keyword)


def test_update_stock_persists_quantity_and_refreshes_timestamp(
    inventory_service: InventoryService,
    storage_service: StorageService,
) -> None:
    """Update only stock quantity and persist a refreshed timestamp."""
    inventory_service.add_product(create_product())
    previous_timestamp = TIMESTAMP

    inventory_service.update_stock("PROD001", 25)

    stored_product = Product.from_dict(storage_service.load_data()["products"][0])
    assert stored_product.quantity == 25
    assert stored_product.updated_at > previous_timestamp


@pytest.mark.parametrize("product_id", [123, None])
def test_update_stock_raises_type_error_for_non_string_id(
    inventory_service: InventoryService,
    product_id: object,
) -> None:
    """Reject non-string product identifiers for stock updates."""
    with pytest.raises(TypeError, match="product_id must be a string"):
        inventory_service.update_stock(product_id, 5)


@pytest.mark.parametrize("product_id", ["", "   "])
def test_update_stock_raises_value_error_for_empty_id(
    inventory_service: InventoryService,
    product_id: str,
) -> None:
    """Reject empty product identifiers for stock updates."""
    with pytest.raises(ValueError, match="product_id cannot be empty"):
        inventory_service.update_stock(product_id, 5)


@pytest.mark.parametrize("quantity", ["5", 5.0, None])
def test_update_stock_raises_type_error_for_non_integer_quantity(
    inventory_service: InventoryService,
    quantity: object,
) -> None:
    """Reject stock quantities that are not integers."""
    with pytest.raises(TypeError, match="quantity must be an integer"):
        inventory_service.update_stock("PROD001", quantity)


def test_update_stock_raises_type_error_for_boolean_quantity(
    inventory_service: InventoryService,
) -> None:
    """Reject boolean values for the stock quantity."""
    with pytest.raises(TypeError, match="quantity must be an integer"):
        inventory_service.update_stock("PROD001", True)


def test_update_stock_raises_value_error_for_negative_quantity(
    inventory_service: InventoryService,
) -> None:
    """Reject negative stock quantities."""
    with pytest.raises(ValueError, match="greater than or equal to 0"):
        inventory_service.update_stock("PROD001", -1)


def test_update_stock_raises_value_error_for_missing_product(
    inventory_service: InventoryService,
) -> None:
    """Reject stock updates for products that are not stored."""
    with pytest.raises(ValueError, match="does not exist"):
        inventory_service.update_stock("MISSING", 5)
