"""Inventory business service interfaces for product operations."""

from models.order_item import OrderItem
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

        if any(
            existing_product.get("id") == product.id
            for existing_product in products
        ):
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
                product.update_timestamp()
                products[index] = product.to_dict()
                self._storage_service.save_data(data)
                return

        raise ValueError(f"Product with ID '{product.id}' does not exist.")

    def delete_product(self, product_id: str) -> None:
        """Remove a product from the inventory.

        Args:
            product_id: Unique identifier of the product to remove.

        Raises:
            TypeError: If product_id is not a string.
            ValueError: If product_id is empty after stripping whitespace or no
                product exists with the specified identifier.
        """
        if not isinstance(product_id, str):
            raise TypeError("product_id must be a string.")

        product_id = product_id.strip()
        if not product_id:
            raise ValueError("product_id cannot be empty.")

        data = self._storage_service.load_data()
        products = data["products"]

        for index, product_data in enumerate(products):
            if product_data.get("id") == product_id:
                del products[index]
                self._storage_service.save_data(data)
                return

        raise ValueError(f"Product with ID '{product_id}' does not exist.")

    def search_products(self, keyword: str) -> list[Product]:
        """Find products that match a keyword.

        Args:
            keyword: Text used to search the product inventory.

        Returns:
            Products that match the provided keyword.

        Raises:
            TypeError: If keyword is not a string.
            ValueError: If keyword is empty after stripping whitespace.
        """
        if not isinstance(keyword, str):
            raise TypeError("keyword must be a string.")

        keyword = keyword.strip()
        if not keyword:
            raise ValueError("keyword cannot be empty.")

        normalized_keyword = keyword.casefold()
        data = self._storage_service.load_data()
        products = data["products"]
        matching_products: list[Product] = []

        for product_data in products:
            searchable_values = (
                product_data.get("id", ""),
                product_data.get("name", ""),
                product_data.get("category", ""),
                product_data.get("supplier", ""),
            )
            if any(
                normalized_keyword in str(value).casefold()
                for value in searchable_values
            ):
                matching_products.append(Product.from_dict(product_data))

        return matching_products

    def update_stock(self, product_id: str, quantity: int) -> None:
        """Update the stock quantity for a product.

        Args:
            product_id: Unique identifier of the product to update.
            quantity: New stock quantity for the product.

        Raises:
            TypeError: If product_id is not a string or quantity is not an integer.
            ValueError: If product_id is empty, quantity is negative, or the
                product does not exist.
        """
        if not isinstance(product_id, str):
            raise TypeError("product_id must be a string.")

        product_id = product_id.strip()
        if not product_id:
            raise ValueError("product_id cannot be empty.")

        if isinstance(quantity, bool) or not isinstance(quantity, int):
            raise TypeError("quantity must be an integer.")
        if quantity < 0:
            raise ValueError("quantity must be greater than or equal to 0.")

        data = self._storage_service.load_data()
        products = data["products"]

        for index, product_data in enumerate(products):
            if product_data.get("id") == product_id:
                product = Product.from_dict(product_data)
                product.quantity = quantity
                product.update_timestamp()
                products[index] = product.to_dict()
                self._storage_service.save_data(data)
                return

        raise ValueError(f"Product with ID '{product_id}' does not exist.")

    def deduct_stock(self, items: list[OrderItem]) -> None:
        """Deduct the quantities requested by order items.

        Args:
            items: Order items whose quantities should be deducted.

        Raises:
            TypeError: If items is not a list of OrderItem instances.
            ValueError: If an item requests an invalid quantity, a product does
                not exist, or available inventory is insufficient.
        """
        self._adjust_stock_for_items(items, -1)

    def restore_stock(self, items: list[OrderItem]) -> None:
        """Restore the quantities associated with order items.

        Args:
            items: Order items whose quantities should be restored.

        Raises:
            TypeError: If items is not a list of OrderItem instances.
            ValueError: If an item requests an invalid quantity or a product
                does not exist.
        """
        self._adjust_stock_for_items(items, 1)

    def _adjust_stock_for_items(
        self,
        items: list[OrderItem],
        direction: int,
    ) -> None:
        """Apply a validated stock adjustment for all supplied order items.

        Args:
            items: Order items used to determine stock quantities.
            direction: Multiplier that indicates deduction or restoration.

        Raises:
            TypeError: If items is not a list of OrderItem instances.
            ValueError: If an item requests an invalid quantity, a product does
                not exist, or available inventory is insufficient.
        """
        if not isinstance(items, list):
            raise TypeError("items must be a list of OrderItem instances.")
        if any(not isinstance(item, OrderItem) for item in items):
            raise TypeError("items must be a list of OrderItem instances.")

        requested_quantities: dict[str, int] = {}
        for item in items:
            if item.quantity <= 0:
                raise ValueError(
                    "Order item quantity must be greater than 0."
                )
            requested_quantities[item.product_id] = (
                requested_quantities.get(item.product_id, 0) + item.quantity
            )

        data = self._storage_service.load_data()
        products = data["products"]
        product_records = {
            product_data.get("id"): (index, Product.from_dict(product_data))
            for index, product_data in enumerate(products)
        }

        for product_id, requested_quantity in requested_quantities.items():
            product_record = product_records.get(product_id)
            if product_record is None:
                raise ValueError(f"Product with ID '{product_id}' does not exist.")

            _, product = product_record
            if direction < 0 and product.quantity < requested_quantity:
                raise ValueError(
                    f"Insufficient stock for product '{product.name}'. "
                    f"Available: {product.quantity}. "
                    f"Requested: {requested_quantity}."
                )

        for product_id, requested_quantity in requested_quantities.items():
            index, product = product_records[product_id]
            product.quantity += direction * requested_quantity
            product.update_timestamp()
            products[index] = product.to_dict()

        self._storage_service.save_data(data)
