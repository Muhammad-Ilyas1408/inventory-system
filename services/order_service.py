"""Order business service for order-related operations."""

from models.customer import Customer
from models.order import Order
from models.order_item import OrderItem
from models.product import Product
from services.storage_service import StorageService


class OrderService:
    """Coordinate order-related business operations."""

    def __init__(self, storage_service: StorageService) -> None:
        """Initialize the service with its persistence dependency.

        Args:
            storage_service: Service used to persist order data.

        Raises:
            TypeError: If storage_service is not a StorageService instance.
        """
        if not isinstance(storage_service, StorageService):
            raise TypeError(
                "storage_service must be a StorageService instance, "
                f"got {type(storage_service).__name__}."
            )

        self._storage_service = storage_service

    def create_order(self, order: Order) -> None:
        """Create an order and deduct the required inventory quantities.

        Args:
            order: Order to create.

        Raises:
            TypeError: If order is not an Order instance.
            ValueError: If the order is duplicate, references invalid entities,
                or requests insufficient inventory.
        """
        if not isinstance(order, Order):
            raise TypeError("order must be an instance of Order.")

        data = self._storage_service.load_data()
        orders = data["orders"]
        customers = data["customers"]
        products = data["products"]

        if any(existing_order.get("id") == order.id for existing_order in orders):
            raise ValueError(f"Order with ID '{order.id}' already exists.")

        customer_data = next(
            (
                customer
                for customer in customers
                if customer.get("id") == order.customer_id
            ),
            None,
        )
        if customer_data is None:
            raise ValueError(f"Customer with ID '{order.customer_id}' does not exist.")
        Customer.from_dict(customer_data)

        product_records: dict[str, tuple[int, Product]] = {}
        for index, product_data in enumerate(products):
            product = Product.from_dict(product_data)
            product_records[product.id] = (index, product)

        order_items: list[OrderItem] = order.items
        requested_quantities: dict[str, int] = {}
        for item in order_items:
            requested_quantities[item.product_id] = (
                requested_quantities.get(item.product_id, 0) + item.quantity
            )

        for product_id, requested_quantity in requested_quantities.items():
            product_record = product_records.get(product_id)
            if product_record is None:
                raise ValueError(f"Product with ID '{product_id}' does not exist.")

            _, product = product_record
            if product.quantity < requested_quantity:
                raise ValueError(f"Insufficient stock for product ID '{product_id}'.")

        for product_id, requested_quantity in requested_quantities.items():
            index, product = product_records[product_id]
            product.quantity -= requested_quantity
            product.update_timestamp()
            products[index] = product.to_dict()

        order.update_timestamp()
        orders.append(order.to_dict())
        self._storage_service.save_data(data)

    def get_order_by_id(self, order_id: str) -> Order | None:
        """Retrieve an order by its unique identifier.

        Args:
            order_id: Unique identifier of the order to retrieve.

        Returns:
            The matching order, or None when no order has the identifier.

        Raises:
            TypeError: If order_id is not a string.
            ValueError: If order_id is empty after stripping whitespace.
        """
        if not isinstance(order_id, str):
            raise TypeError("order_id must be a string.")

        order_id = order_id.strip()
        if not order_id:
            raise ValueError("order_id cannot be empty.")

        data = self._storage_service.load_data()
        orders = data["orders"]
        for order_data in orders:
            if order_data.get("id") == order_id:
                return Order.from_dict(order_data)

        return None

    def get_all_orders(self) -> list[Order]:
        """Retrieve all orders in the system.

        Returns:
            All orders currently stored in the system.
        """
        data = self._storage_service.load_data()
        return [Order.from_dict(order_data) for order_data in data["orders"]]

    def update_order(self, order: Order) -> None:
        """Update an existing order in the system.

        Args:
            order: Order containing the updated data.

        Raises:
            TypeError: If order is not an Order instance.
            ValueError: If no order exists with the same identifier.
        """
        if not isinstance(order, Order):
            raise TypeError("order must be an instance of Order.")

        data = self._storage_service.load_data()
        orders = data["orders"]

        for index, existing_order in enumerate(orders):
            if existing_order.get("id") == order.id:
                order.update_timestamp()
                orders[index] = order.to_dict()
                self._storage_service.save_data(data)
                return

        raise ValueError(f"Order with ID '{order.id}' does not exist.")

    def delete_order(self, order_id: str) -> None:
        """Remove an order and restore its inventory quantities.

        Args:
            order_id: Unique identifier of the order to remove.

        Raises:
            TypeError: If order_id is not a string.
            ValueError: If order_id is empty, the order does not exist, or a
                referenced product does not exist.
        """
        if not isinstance(order_id, str):
            raise TypeError("order_id must be a string.")

        order_id = order_id.strip()
        if not order_id:
            raise ValueError("order_id cannot be empty.")

        data = self._storage_service.load_data()
        orders = data["orders"]
        products = data["products"]

        order_index = next(
            (
                index
                for index, order_data in enumerate(orders)
                if order_data.get("id") == order_id
            ),
            None,
        )
        if order_index is None:
            raise ValueError(f"Order with ID '{order_id}' does not exist.")

        order = Order.from_dict(orders[order_index])
        product_records: dict[str, tuple[int, Product]] = {}
        for index, product_data in enumerate(products):
            product = Product.from_dict(product_data)
            product_records[product.id] = (index, product)

        restored_quantities: dict[str, int] = {}
        for item in order.items:
            restored_quantities[item.product_id] = (
                restored_quantities.get(item.product_id, 0) + item.quantity
            )

        for product_id in restored_quantities:
            if product_id not in product_records:
                raise ValueError(f"Product with ID '{product_id}' does not exist.")

        for product_id, restored_quantity in restored_quantities.items():
            index, product = product_records[product_id]
            product.quantity += restored_quantity
            product.update_timestamp()
            products[index] = product.to_dict()

        del orders[order_index]
        self._storage_service.save_data(data)

    def search_orders(self, keyword: str) -> list[Order]:
        """Find orders that match a keyword.

        Args:
            keyword: Text used to search the order system.

        Returns:
            Orders that match the provided keyword.

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
        orders = data["orders"]
        matching_orders: list[Order] = []

        for order_data in orders:
            searchable_values = (
                order_data.get("id", ""),
                order_data.get("customer_id", ""),
                order_data.get("status", ""),
            )
            if any(
                normalized_keyword in str(value).casefold()
                for value in searchable_values
            ):
                matching_orders.append(Order.from_dict(order_data))

        return matching_orders

    def get_orders_by_customer(self, customer_id: str) -> list[Order]:
        """Retrieve all orders placed by a customer.

        Args:
            customer_id: Unique identifier of the customer whose orders to retrieve.

        Returns:
            Orders associated with the provided customer identifier.

        Raises:
            TypeError: If customer_id is not a string.
            ValueError: If customer_id is empty after stripping whitespace.
        """
        if not isinstance(customer_id, str):
            raise TypeError("customer_id must be a string.")

        customer_id = customer_id.strip()
        if not customer_id:
            raise ValueError("customer_id cannot be empty.")

        data = self._storage_service.load_data()
        return [
            Order.from_dict(order_data)
            for order_data in data["orders"]
            if order_data.get("customer_id") == customer_id
        ]

    def calculate_order_total(self, order_id: str) -> float:
        """Calculate the total price of an order.

        Args:
            order_id: Unique identifier of the order to total.

        Returns:
            The sum of every order item subtotal.

        Raises:
            TypeError: If order_id is not a string.
            ValueError: If order_id is empty after stripping whitespace or the
                order does not exist.
        """
        order = self.get_order_by_id(order_id)
        if order is None:
            raise ValueError(f"Order with ID '{order_id.strip()}' does not exist.")

        return order.total
