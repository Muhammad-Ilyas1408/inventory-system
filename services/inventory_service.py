"""Inventory business service interfaces for product operations."""

from models.product import Product
from services.storage_service import StorageService


class InventoryService:
    """Coordinate product-related inventory operations."""

    def __init__(self, storage_service: StorageService) -> None:
        """Initialize the service with its persistence dependency.

        Args:
            storage_service: Service used to persist inventory data.

        Raises:
            TypeError: If storage_service is not a StorageService instance.
        """
        if not isinstance(storage_service, StorageService):
            raise TypeError(
                "storage_service must be a StorageService instance, "
                f"got {type(storage_service).__name__}."
            )

        self._storage_service = storage_service

    def add_product(self, product: Product) -> None:
        """Add a product to the inventory.

        Args:
            product: Product to add.

        Raises:
            TypeError: If product is not a Product instance.
            ValueError: If a product with the same identifier already exists.
        """
        if not isinstance(product, Product):
            raise TypeError("product must be an instance of Product.")

        data = self._storage_service.load_data()
        products = data["products"]

        if any(existing_product.get("id") == product.id for existing_product in products):
            raise ValueError(f"Product with ID '{product.id}' already exists.")

        products.append(product.to_dict())
        self._storage_service.save_data(data)

    def get_product_by_id(self, product_id: str) -> Product | None:
        """Retrieve a product by its unique identifier.

        Args:
            product_id: Unique identifier of the product to retrieve.

        Returns:
            The matching product, or None when no product has the identifier.

        Raises:
            TypeError: If product_id is not a string.
            ValueError: If product_id is empty after stripping whitespace.
        """
        if not isinstance(product_id, str):
            raise TypeError("product_id must be a string.")

        product_id = product_id.strip()
        if not product_id:
            raise ValueError("product_id cannot be empty.")

        data = self._storage_service.load_data()
        products = data["products"]
        for product_data in products:
            if product_data.get("id") == product_id:
                return Product.from_dict(product_data)

        return None

    def get_all_products(self) -> list[Product]:
        """Retrieve all products in the inventory.

        Returns:
            All products currently stored in the inventory.
        """
        data = self._storage_service.load_data()
        return [Product.from_dict(product_data) for product_data in data["products"]]

    def update_product(self, product: Product) -> None:
        """Update an existing product in the inventory.

        Args:
            product: Product containing the updated data.

        Raises:
            TypeError: If product is not an instance of Product.
            ValueError: If no product exists with the same identifier.
        """
        if not isinstance(product, Product):
            raise TypeError("product must be an instance of Product.")

        data = self._storage_service.load_data()
        products = data["products"]

        for index, existing_product in enumerate(products):
            if existing_product.get("id") == product.id:
                products[index] = product.to_dict()
                self._storage_service.save_data(data)
                return

        raise ValueError(f"Product with ID '{product.id}' does not exist.")

    def delete_product(self, product_id: str) -> None:
        """Remove a product from the inventory.

        Args:
            product_id: Unique identifier of the product to remove.

        Raises:
            NotImplementedError: This interface has not been implemented yet.
        """
        raise NotImplementedError

    def search_products(self, keyword: str) -> list[Product]:
        """Find products that match a keyword.

        Args:
            keyword: Text used to search the product inventory.

        Returns:
            Products that match the provided keyword.

        Raises:
            NotImplementedError: This interface has not been implemented yet.
        """
        raise NotImplementedError

    def update_stock(self, product_id: str, quantity: int) -> None:
        """Update the stock quantity for a product.

        Args:
            product_id: Unique identifier of the product to update.
            quantity: New stock quantity for the product.

        Raises:
            NotImplementedError: This interface has not been implemented yet.
        """
        raise NotImplementedError
