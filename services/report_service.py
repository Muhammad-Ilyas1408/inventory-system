"""Read-only reporting service for inventory and sales data."""

from models.invoice import Invoice
from models.product import Product
from services.storage_service import StorageService


class ReportService:
    """Compute read-only summaries from the application data."""

    def __init__(self, storage_service: StorageService) -> None:
        """Initialize the service with its persistence dependency.

        Args:
            storage_service: Service used to read report data.

        Raises:
            TypeError: If storage_service is not a StorageService instance.
        """
        if not isinstance(storage_service, StorageService):
            raise TypeError(
                "storage_service must be a StorageService instance, "
                f"got {type(storage_service).__name__}."
            )

        self._storage_service = storage_service

    def get_inventory_summary(self) -> dict[str, int]:
        """Return summary counts for the current inventory.

        Returns:
            The total product count and the total number of stocked units.
        """
        data = self._storage_service.load_data()
        products = [
            Product.from_dict(product_data)
            for product_data in data["products"]
        ]
        return {
            "total_products": len(products),
            "total_stock": sum(product.quantity for product in products),
        }

    def get_low_stock_products(self, threshold: int = 5) -> list[Product]:
        """Return products whose stock quantity is at or below a threshold.

        Args:
            threshold: Maximum quantity for a product to be considered low stock.

        Returns:
            Products at or below the specified stock threshold.

        Raises:
            TypeError: If threshold is not an integer.
            ValueError: If threshold is negative.
        """
        if isinstance(threshold, bool) or not isinstance(threshold, int):
            raise TypeError("threshold must be an integer.")
        if threshold < 0:
            raise ValueError("threshold must be greater than or equal to 0.")

        data = self._storage_service.load_data()
        products = [
            Product.from_dict(product_data)
            for product_data in data["products"]
        ]
        return [
            product
            for product in products
            if product.quantity <= threshold
        ]

    def get_total_sales(self) -> float:
        """Return the sum of all stored invoice totals.

        Returns:
            The total sales amount, or 0.0 when no invoices exist.
        """
        data = self._storage_service.load_data()
        invoices = [
            Invoice.from_dict(invoice_data)
            for invoice_data in data["invoices"]
        ]
        return sum((invoice.total for invoice in invoices), 0.0)

    def get_total_orders(self) -> int:
        """Return the total number of stored orders.

        Returns:
            The total order count.
        """
        data = self._storage_service.load_data()
        return len(data["orders"])

    def get_total_customers(self) -> int:
        """Return the total number of stored customers.

        Returns:
            The total customer count.
        """
        data = self._storage_service.load_data()
        return len(data["customers"])

    def get_total_invoices(self) -> int:
        """Return the total number of stored invoices.

        Returns:
            The total invoice count.
        """
        data = self._storage_service.load_data()
        return len(data["invoices"])
