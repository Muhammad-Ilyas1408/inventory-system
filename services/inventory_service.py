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
            raise TypeError(f"storage_service must be an instance of StorageService instance, "
                            f"got {type(storage_service).__name__}.")

        self._storage_service = storage_service

    def add_product(self, product: Product) -> None:
        """Add a product to the inventory.

        Args:
            product: Product to add.

        Raises:
            NotImplementedError: This interface has not been implemented yet.
        """
        raise NotImplementedError

    def get_product_by_id(self, product_id: str) -> Product | None:
        """Retrieve a product by its unique identifier.

        Args:
            product_id: Unique identifier of the product to retrieve.

        Returns:
            The matching product, or None when no product has the identifier.

        Raises:
            NotImplementedError: This interface has not been implemented yet.
        """
        raise NotImplementedError

    def get_all_products(self) -> list[Product]:
        """Retrieve all products in the inventory.

        Returns:
            All products currently stored in the inventory.

        Raises:
            NotImplementedError: This interface has not been implemented yet.
        """
        raise NotImplementedError

    def update_product(self, product: Product) -> None:
        """Update an existing product in the inventory.

        Args:
            product: Product containing the updated data.

        Raises:
            NotImplementedError: This interface has not been implemented yet.
        """
        raise NotImplementedError

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
