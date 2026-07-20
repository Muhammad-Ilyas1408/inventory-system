"""Invoice business service for invoice-related operations."""

from datetime import datetime

from models.customer import Customer
from models.invoice import Invoice
from models.order import Order
from services.storage_service import StorageService


class InvoiceService:
    """Coordinate invoice-related business operations."""

    def __init__(self, storage_service: StorageService) -> None:
        """Initialize the service with its persistence dependency.

        Args:
            storage_service: Service used to persist invoice data.

        Raises:
            TypeError: If storage_service is not a StorageService instance.
        """
        if not isinstance(storage_service, StorageService):
            raise TypeError(
                "storage_service must be a StorageService instance, "
                f"got {type(storage_service).__name__}."
            )

        self._storage_service = storage_service

    def create_invoice_from_order(
        self,
        order: Order,
        customer: Customer,
    ) -> None:
        """Create and persist an invoice using existing order data.

        Args:
            order: Persisted order that the invoice represents.
            customer: Customer associated with the order.

        Raises:
            TypeError: If order or customer has an invalid type.
            ValueError: If the order cannot be invoiced.
        """
        if not isinstance(order, Order):
            raise TypeError("order must be an instance of Order.")
        if not isinstance(customer, Customer):
            raise TypeError("customer must be an instance of Customer.")

        invoice = self._build_invoice(
            self._generate_invoice_id(),
            order,
            customer,
        )
        self.create_invoice(invoice)

    def create_invoice_for_order(self, invoice_id: str, order_id: str) -> None:
        """Create an invoice for an existing order using stored data.

        Args:
            invoice_id: Unique identifier assigned to the new invoice.
            order_id: Identifier of the order to invoice.

        Raises:
            TypeError: If invoice_id or order_id is not a string.
            ValueError: If either identifier is empty, the order or customer is
                missing, or the order already has an invoice.
        """
        if not isinstance(invoice_id, str):
            raise TypeError("invoice_id must be a string.")
        if not isinstance(order_id, str):
            raise TypeError("order_id must be a string.")

        invoice_id = invoice_id.strip()
        order_id = order_id.strip()
        if not invoice_id:
            raise ValueError("invoice_id cannot be empty.")
        if not order_id:
            raise ValueError("order_id cannot be empty.")

        data = self._storage_service.load_data()
        order_data = next(
            (
                order
                for order in data["orders"]
                if order.get("id") == order_id
            ),
            None,
        )
        if order_data is None:
            raise ValueError("Order not found.")
        if any(invoice.get("order_id") == order_id for invoice in data["invoices"]):
            raise ValueError(f"Invoice already exists for Order {order_id}.")

        order = Order.from_dict(order_data)
        customer_data = next(
            (
                customer
                for customer in data["customers"]
                if customer.get("id") == order.customer_id
            ),
            None,
        )
        if customer_data is None:
            raise ValueError(
                f"Customer with ID '{order.customer_id}' does not exist."
            )

        invoice = self._build_invoice(
            invoice_id,
            order,
            Customer.from_dict(customer_data),
        )
        self.create_invoice(invoice)

    def _build_invoice(
        self,
        invoice_id: str,
        order: Order,
        customer: Customer,
    ) -> Invoice:
        """Build an invoice from an order and its associated customer.

        Args:
            invoice_id: Unique identifier for the new invoice.
            order: Order represented by the invoice.
            customer: Customer associated with the order.

        Returns:
            An invoice populated with order and customer snapshot data.
        """
        return Invoice(
            id=invoice_id,
            order_id=order.id,
            customer_name=customer.full_name,
            customer_email=customer.email,
            items=order.items,
            subtotal=order.total,
            total=order.total,
            issued_at=datetime.now(),
        )

    def _generate_invoice_id(self) -> str:
        """Generate the next sequential invoice identifier.

        Returns:
            The next available invoice identifier in the ``INV###`` sequence.
        """
        data = self._storage_service.load_data()
        invoice_numbers = [
            int(invoice["id"][3:])
            for invoice in data["invoices"]
            if invoice.get("id", "").startswith("INV")
            and invoice["id"][3:].isdigit()
        ]
        return f"INV{max(invoice_numbers, default=0) + 1:03d}"

    def create_invoice(self, invoice: Invoice) -> None:
        """Create and persist an invoice for an existing order.

        Args:
            invoice: Invoice to create.

        Raises:
            TypeError: If invoice is not an Invoice instance.
            ValueError: If the invoice is duplicate or its order does not exist.
        """
        if not isinstance(invoice, Invoice):
            raise TypeError("invoice must be an instance of Invoice.")

        data = self._storage_service.load_data()
        invoices = data["invoices"]
        orders = data["orders"]

        if any(
            existing_invoice.get("id") == invoice.id
            for existing_invoice in invoices
        ):
            raise ValueError(f"Invoice with ID '{invoice.id}' already exists.")

        if any(
            existing_invoice.get("order_id") == invoice.order_id
            for existing_invoice in invoices
        ):
            raise ValueError(
                f"Invoice already exists for Order {invoice.order_id}."
            )

        if not any(order.get("id") == invoice.order_id for order in orders):
            raise ValueError(f"Order with ID '{invoice.order_id}' does not exist.")

        invoices.append(invoice.to_dict())
        self._storage_service.save_data(data)

    def get_invoice_by_id(self, invoice_id: str) -> Invoice | None:
        """Retrieve an invoice by its unique identifier.

        Args:
            invoice_id: Unique identifier of the invoice to retrieve.

        Returns:
            The matching invoice, or None when no invoice has the identifier.

        Raises:
            TypeError: If invoice_id is not a string.
            ValueError: If invoice_id is empty after stripping whitespace.
        """
        if not isinstance(invoice_id, str):
            raise TypeError("invoice_id must be a string.")

        invoice_id = invoice_id.strip()
        if not invoice_id:
            raise ValueError("invoice_id cannot be empty.")

        data = self._storage_service.load_data()
        for invoice_data in data["invoices"]:
            if invoice_data.get("id") == invoice_id:
                return Invoice.from_dict(invoice_data)

        return None

    def get_all_invoices(self) -> list[Invoice]:
        """Retrieve all invoices in the system.

        Returns:
            All invoices currently stored in the system.
        """
        data = self._storage_service.load_data()
        return [
            Invoice.from_dict(invoice_data)
            for invoice_data in data["invoices"]
        ]

    def update_invoice(self, invoice: Invoice) -> None:
        """Update an existing invoice in the system.

        Args:
            invoice: Invoice containing the updated data.

        Raises:
            TypeError: If invoice is not an Invoice instance.
            ValueError: If no invoice exists with the same identifier.
        """
        if not isinstance(invoice, Invoice):
            raise TypeError("invoice must be an instance of Invoice.")

        data = self._storage_service.load_data()
        invoices = data["invoices"]

        for index, existing_invoice in enumerate(invoices):
            if existing_invoice.get("id") == invoice.id:
                invoices[index] = invoice.to_dict()
                self._storage_service.save_data(data)
                return

        raise ValueError(f"Invoice with ID '{invoice.id}' does not exist.")

    def delete_invoice(self, invoice_id: str) -> None:
        """Remove an invoice from the system.

        Args:
            invoice_id: Unique identifier of the invoice to remove.

        Raises:
            TypeError: If invoice_id is not a string.
            ValueError: If invoice_id is empty after stripping whitespace or no
                invoice exists with the specified identifier.
        """
        if not isinstance(invoice_id, str):
            raise TypeError("invoice_id must be a string.")

        invoice_id = invoice_id.strip()
        if not invoice_id:
            raise ValueError("invoice_id cannot be empty.")

        data = self._storage_service.load_data()
        invoices = data["invoices"]

        for index, invoice_data in enumerate(invoices):
            if invoice_data.get("id") == invoice_id:
                del invoices[index]
                self._storage_service.save_data(data)
                return

        raise ValueError(f"Invoice with ID '{invoice_id}' does not exist.")

    def search_invoices(self, keyword: str) -> list[Invoice]:
        """Find invoices that match a keyword.

        Args:
            keyword: Text used to search the invoice system.

        Returns:
            Invoices that match the provided keyword.

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
        order_details = {
            order_data.get("id"): (
                order_data.get("customer_id", ""),
                order_data.get("status", ""),
            )
            for order_data in data["orders"]
        }
        matching_invoices: list[Invoice] = []

        for invoice_data in data["invoices"]:
            customer_id, status = order_details.get(
                invoice_data.get("order_id"),
                ("", ""),
            )
            searchable_values = (
                invoice_data.get("id", ""),
                invoice_data.get("order_id", ""),
                customer_id,
                status,
            )
            if any(
                normalized_keyword in str(value).casefold()
                for value in searchable_values
            ):
                matching_invoices.append(Invoice.from_dict(invoice_data))

        return matching_invoices

    def get_invoices_by_customer(self, customer_id: str) -> list[Invoice]:
        """Retrieve all invoices associated with a customer.

        Args:
            customer_id: Unique identifier of the customer whose invoices to retrieve.

        Returns:
            Invoices associated with the provided customer identifier.

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
        customer_order_ids = {
            order_data.get("id")
            for order_data in data["orders"]
            if order_data.get("customer_id") == customer_id
        }
        return [
            Invoice.from_dict(invoice_data)
            for invoice_data in data["invoices"]
            if invoice_data.get("order_id") in customer_order_ids
        ]

    def get_invoice_by_order(self, order_id: str) -> Invoice | None:
        """Retrieve an invoice by its associated order identifier.

        Args:
            order_id: Unique identifier of the invoice's associated order.

        Returns:
            The matching invoice, or None when no invoice references the order.

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
        for invoice_data in data["invoices"]:
            if invoice_data.get("order_id") == order_id:
                return Invoice.from_dict(invoice_data)

        return None
