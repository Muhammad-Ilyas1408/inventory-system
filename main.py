"""Command-line interface for the Inventory Management System."""

from collections.abc import Callable
from datetime import datetime

from models.customer import Customer
from models.enums import OrderStatus
from models.invoice import Invoice
from models.order import Order
from models.order_item import OrderItem
from models.product import Product
from services.customer_service import CustomerService
from services.inventory_service import InventoryService
from services.invoice_service import InvoiceService
from services.order_service import OrderService
from services.report_service import ReportService
from services.storage_service import StorageService


def _display_menu(title: str, options: list[tuple[str, str]]) -> None:
    """Display a formatted menu.

    Args:
        title: Heading displayed above the menu options.
        options: Menu option identifiers and descriptions.
    """
    print("\n" + "=" * 41)
    print(title)
    print("=" * 41)
    for option, description in options:
        print(f"{option}. {description}")


def _get_selection(valid_options: set[str]) -> str | None:
    """Read and validate a menu selection.

    Args:
        valid_options: Permitted selection values.

    Returns:
        The validated selection, or None when the input is invalid.
    """
    selection = input("Select an option: ").strip()
    if selection not in valid_options:
        print("Invalid selection. Please choose a listed option.")
        return None
    return selection


def _run_action(action: Callable[[], None]) -> None:
    """Run a CLI action and display user-friendly errors.

    Args:
        action: User-initiated operation to execute.
    """
    try:
        action()
    except (TypeError, ValueError) as error:
        print(f"Error: {error}")
    except Exception:
        print("An unexpected error occurred. Please try again.")


def _prompt_text(label: str, default: str | None = None) -> str:
    """Prompt for text, optionally using a displayed default value.

    Args:
        label: Description of the requested value.
        default: Value returned when the user submits blank input.

    Returns:
        The entered text or the provided default.
    """
    prompt = f"{label}"
    if default is not None:
        prompt += f" [{default}]"
    value = input(f"{prompt}: ").strip()
    return value if value or default is None else default


def _prompt_order_items() -> list[OrderItem]:
    """Collect one or more order items from the user.

    Returns:
        Order items entered by the user.
    """
    items: list[OrderItem] = []
    while True:
        print("\nOrder Item")
        items.append(
            OrderItem(
                product_id=_prompt_text("Product ID"),
                product_name=_prompt_text("Product Name"),
                unit_price=float(_prompt_text("Unit Price")),
                quantity=int(_prompt_text("Quantity")),
            )
        )
        if _prompt_text("Add another item? (y/n)", "n").casefold() != "y":
            return items


def _display_product(product: Product) -> None:
    """Display a product in a readable format.

    Args:
        product: Product to display.
    """
    print("-" * 39)
    print(f"ID: {product.id}")
    print(f"Name: {product.name}")
    print(f"Category: {product.category}")
    print(f"Price: {product.price:.2f}")
    print(f"Quantity: {product.quantity}")
    print(f"Supplier: {product.supplier}")


def _display_customer(customer: Customer) -> None:
    """Display a customer in a readable format.

    Args:
        customer: Customer to display.
    """
    print("-" * 39)
    print(f"ID: {customer.id}")
    print(f"Name: {customer.full_name}")
    print(f"Email: {customer.email}")
    print(f"Phone: {customer.phone}")
    print(f"Address: {customer.address}")


def _display_order(order: Order) -> None:
    """Display an order in a readable format.

    Args:
        order: Order to display.
    """
    print("-" * 39)
    print(f"ID: {order.id}")
    print(f"Customer ID: {order.customer_id}")
    print(f"Status: {order.status.value}")
    print(f"Total: {order.total:.2f}")
    for item in order.items:
        print(f"  - {item.product_name}: {item.quantity} x {item.unit_price:.2f}")


def _display_invoice(invoice: Invoice) -> None:
    """Display an invoice in a readable format.

    Args:
        invoice: Invoice to display.
    """
    print("-" * 39)
    print(f"ID: {invoice.id}")
    print(f"Order ID: {invoice.order_id}")
    print(f"Customer: {invoice.customer_name}")
    print(f"Email: {invoice.customer_email}")
    print(f"Subtotal: {invoice.subtotal:.2f}")
    print(f"Total: {invoice.total:.2f}")
    print(f"Issued At: {invoice.issued_at.isoformat(sep=' ', timespec='seconds')}")


def _add_product(service: InventoryService) -> None:
    """Collect and add a product through InventoryService.

    Args:
        service: Inventory service used to add the product.
    """
    product = Product(
        id=_prompt_text("ID"),
        name=_prompt_text("Name"),
        category=_prompt_text("Category"),
        price=float(_prompt_text("Price")),
        quantity=int(_prompt_text("Quantity")),
        supplier=_prompt_text("Supplier"),
    )
    service.add_product(product)
    print("Product added successfully.")


def _view_products(service: InventoryService) -> None:
    """Display all products through InventoryService.

    Args:
        service: Inventory service used to retrieve products.
    """
    products = service.get_all_products()
    if not products:
        print("No products found.")
        return
    for product in products:
        _display_product(product)


def _search_products(service: InventoryService) -> None:
    """Search and display products.

    Args:
        service: Inventory service used to search products.
    """
    products = service.search_products(_prompt_text("Search keyword"))
    if not products:
        print("No matching products found.")
        return
    for product in products:
        _display_product(product)


def _update_product(service: InventoryService) -> None:
    """Collect and update an existing product.

    Args:
        service: Inventory service used to update the product.
    """
    product_id = _prompt_text("Product ID")
    existing = service.get_product_by_id(product_id)
    if existing is None:
        print("Product not found.")
        return
    product = Product(
        id=existing.id,
        name=_prompt_text("Name", existing.name),
        category=_prompt_text("Category", existing.category),
        price=float(_prompt_text("Price", str(existing.price))),
        quantity=int(_prompt_text("Quantity", str(existing.quantity))),
        supplier=_prompt_text("Supplier", existing.supplier),
        created_at=existing.created_at,
        updated_at=existing.updated_at,
    )
    service.update_product(product)
    print("Product updated successfully.")


def _delete_product(service: InventoryService) -> None:
    """Delete a product through InventoryService.

    Args:
        service: Inventory service used to delete the product.
    """
    service.delete_product(_prompt_text("Product ID"))
    print("Product deleted successfully.")


def product_menu(service: InventoryService) -> None:
    """Run the product management menu.

    Args:
        service: Inventory service used by menu actions.
    """
    actions: dict[str, Callable[[], None]] = {
        "1": lambda: _add_product(service),
        "2": lambda: _view_products(service),
        "3": lambda: _search_products(service),
        "4": lambda: _update_product(service),
        "5": lambda: _delete_product(service),
    }
    while True:
        _display_menu(
            "Product Management",
            [
                ("1", "Add Product"),
                ("2", "View All Products"),
                ("3", "Search Product"),
                ("4", "Update Product"),
                ("5", "Delete Product"),
                ("0", "Back"),
            ],
        )
        selection = _get_selection(set(actions) | {"0"})
        if selection == "0":
            return
        if selection is not None:
            _run_action(actions[selection])


def _add_customer(service: CustomerService) -> None:
    """Collect and add a customer through CustomerService.

    Args:
        service: Customer service used to add the customer.
    """
    customer = Customer(
        id=_prompt_text("ID"),
        first_name=_prompt_text("First Name"),
        last_name=_prompt_text("Last Name"),
        email=_prompt_text("Email"),
        phone=_prompt_text("Phone"),
        address=_prompt_text("Address"),
    )
    service.add_customer(customer)
    print("Customer added successfully.")


def _view_customers(service: CustomerService) -> None:
    """Display all customers through CustomerService.

    Args:
        service: Customer service used to retrieve customers.
    """
    customers = service.get_all_customers()
    if not customers:
        print("No customers found.")
        return
    for customer in customers:
        _display_customer(customer)


def _search_customers(service: CustomerService) -> None:
    """Search and display customers.

    Args:
        service: Customer service used to search customers.
    """
    customers = service.search_customers(_prompt_text("Search keyword"))
    if not customers:
        print("No matching customers found.")
        return
    for customer in customers:
        _display_customer(customer)


def _update_customer(service: CustomerService) -> None:
    """Collect and update an existing customer.

    Args:
        service: Customer service used to update the customer.
    """
    customer_id = _prompt_text("Customer ID")
    existing = service.get_customer_by_id(customer_id)
    if existing is None:
        print("Customer not found.")
        return
    customer = Customer(
        id=existing.id,
        first_name=_prompt_text("First Name", existing.first_name),
        last_name=_prompt_text("Last Name", existing.last_name),
        email=_prompt_text("Email", existing.email),
        phone=_prompt_text("Phone", existing.phone),
        address=_prompt_text("Address", existing.address),
        created_at=existing.created_at,
        updated_at=existing.updated_at,
    )
    service.update_customer(customer)
    print("Customer updated successfully.")


def _delete_customer(service: CustomerService) -> None:
    """Delete a customer through CustomerService.

    Args:
        service: Customer service used to delete the customer.
    """
    service.delete_customer(_prompt_text("Customer ID"))
    print("Customer deleted successfully.")


def customer_menu(service: CustomerService) -> None:
    """Run the customer management menu.

    Args:
        service: Customer service used by menu actions.
    """
    actions: dict[str, Callable[[], None]] = {
        "1": lambda: _add_customer(service),
        "2": lambda: _view_customers(service),
        "3": lambda: _search_customers(service),
        "4": lambda: _update_customer(service),
        "5": lambda: _delete_customer(service),
    }
    while True:
        _display_menu(
            "Customer Management",
            [
                ("1", "Add Customer"),
                ("2", "View All Customers"),
                ("3", "Search Customer"),
                ("4", "Update Customer"),
                ("5", "Delete Customer"),
                ("0", "Back"),
            ],
        )
        selection = _get_selection(set(actions) | {"0"})
        if selection == "0":
            return
        if selection is not None:
            _run_action(actions[selection])


def _create_order(service: OrderService) -> None:
    """Collect and create an order through OrderService.

    Args:
        service: Order service used to create the order.
    """
    status = OrderStatus(_prompt_text("Status", OrderStatus.PENDING.value).upper())
    order = Order(
        id=_prompt_text("Order ID"),
        customer_id=_prompt_text("Customer ID"),
        items=_prompt_order_items(),
        status=status,
    )
    service.create_order(order)
    print("Order created successfully.")


def _view_orders(service: OrderService) -> None:
    """Display all orders through OrderService.

    Args:
        service: Order service used to retrieve orders.
    """
    orders = service.get_all_orders()
    if not orders:
        print("No orders found.")
        return
    for order in orders:
        _display_order(order)


def _search_orders(service: OrderService) -> None:
    """Search and display orders.

    Args:
        service: Order service used to search orders.
    """
    orders = service.search_orders(_prompt_text("Search keyword"))
    if not orders:
        print("No matching orders found.")
        return
    for order in orders:
        _display_order(order)


def _view_customer_orders(service: OrderService) -> None:
    """Display all orders for a customer.

    Args:
        service: Order service used to retrieve customer orders.
    """
    orders = service.get_orders_by_customer(_prompt_text("Customer ID"))
    if not orders:
        print("No orders found for this customer.")
        return
    for order in orders:
        _display_order(order)


def _delete_order(service: OrderService) -> None:
    """Delete an order through OrderService.

    Args:
        service: Order service used to delete the order.
    """
    service.delete_order(_prompt_text("Order ID"))
    print("Order deleted successfully.")


def _calculate_order_total(service: OrderService) -> None:
    """Calculate and display an order total.

    Args:
        service: Order service used to calculate the total.
    """
    total = service.calculate_order_total(_prompt_text("Order ID"))
    print(f"Order total: {total:.2f}")


def order_menu(service: OrderService) -> None:
    """Run the order management menu.

    Args:
        service: Order service used by menu actions.
    """
    actions: dict[str, Callable[[], None]] = {
        "1": lambda: _create_order(service),
        "2": lambda: _view_orders(service),
        "3": lambda: _search_orders(service),
        "4": lambda: _view_customer_orders(service),
        "5": lambda: _delete_order(service),
        "6": lambda: _calculate_order_total(service),
    }
    while True:
        _display_menu(
            "Order Management",
            [
                ("1", "Create Order"),
                ("2", "View All Orders"),
                ("3", "Search Order"),
                ("4", "View Customer Orders"),
                ("5", "Delete Order"),
                ("6", "Calculate Order Total"),
                ("0", "Back"),
            ],
        )
        selection = _get_selection(set(actions) | {"0"})
        if selection == "0":
            return
        if selection is not None:
            _run_action(actions[selection])


def _create_invoice(service: InvoiceService) -> None:
    """Collect and create an invoice through InvoiceService.

    Args:
        service: Invoice service used to create the invoice.
    """
    issued_at_text = _prompt_text("Issued At (ISO format, blank for now)", "")
    issued_at = (
        datetime.fromisoformat(issued_at_text)
        if issued_at_text
        else datetime.now()
    )
    invoice = Invoice(
        id=_prompt_text("Invoice ID"),
        order_id=_prompt_text("Order ID"),
        customer_name=_prompt_text("Customer Name"),
        customer_email=_prompt_text("Customer Email"),
        items=_prompt_order_items(),
        subtotal=float(_prompt_text("Subtotal")),
        total=float(_prompt_text("Total")),
        issued_at=issued_at,
    )
    service.create_invoice(invoice)
    print("Invoice created successfully.")


def _view_invoices(service: InvoiceService) -> None:
    """Display all invoices through InvoiceService.

    Args:
        service: Invoice service used to retrieve invoices.
    """
    invoices = service.get_all_invoices()
    if not invoices:
        print("No invoices found.")
        return
    for invoice in invoices:
        _display_invoice(invoice)


def _search_invoices(service: InvoiceService) -> None:
    """Search and display invoices.

    Args:
        service: Invoice service used to search invoices.
    """
    invoices = service.search_invoices(_prompt_text("Search keyword"))
    if not invoices:
        print("No matching invoices found.")
        return
    for invoice in invoices:
        _display_invoice(invoice)


def _view_invoice_by_order(service: InvoiceService) -> None:
    """Display an invoice for a selected order.

    Args:
        service: Invoice service used to retrieve the invoice.
    """
    invoice = service.get_invoice_by_order(_prompt_text("Order ID"))
    if invoice is None:
        print("No invoice found for this order.")
        return
    _display_invoice(invoice)


def _view_customer_invoices(service: InvoiceService) -> None:
    """Display invoices associated with a customer.

    Args:
        service: Invoice service used to retrieve customer invoices.
    """
    invoices = service.get_invoices_by_customer(_prompt_text("Customer ID"))
    if not invoices:
        print("No invoices found for this customer.")
        return
    for invoice in invoices:
        _display_invoice(invoice)


def _delete_invoice(service: InvoiceService) -> None:
    """Delete an invoice through InvoiceService.

    Args:
        service: Invoice service used to delete the invoice.
    """
    service.delete_invoice(_prompt_text("Invoice ID"))
    print("Invoice deleted successfully.")


def invoice_menu(service: InvoiceService) -> None:
    """Run the invoice management menu.

    Args:
        service: Invoice service used by menu actions.
    """
    actions: dict[str, Callable[[], None]] = {
        "1": lambda: _create_invoice(service),
        "2": lambda: _view_invoices(service),
        "3": lambda: _search_invoices(service),
        "4": lambda: _view_invoice_by_order(service),
        "5": lambda: _view_customer_invoices(service),
        "6": lambda: _delete_invoice(service),
    }
    while True:
        _display_menu(
            "Invoice Management",
            [
                ("1", "Create Invoice"),
                ("2", "View All Invoices"),
                ("3", "Search Invoice"),
                ("4", "View Invoice By Order"),
                ("5", "View Customer Invoices"),
                ("6", "Delete Invoice"),
                ("0", "Back"),
            ],
        )
        selection = _get_selection(set(actions) | {"0"})
        if selection == "0":
            return
        if selection is not None:
            _run_action(actions[selection])


def _show_inventory_summary(service: ReportService) -> None:
    """Display the inventory summary.

    Args:
        service: Report service used to retrieve the summary.
    """
    summary = service.get_inventory_summary()
    print(f"Total Products: {summary['total_products']}")
    print(f"Total Stock: {summary['total_stock']}")


def _show_low_stock_products(service: ReportService) -> None:
    """Display products at or below a chosen stock threshold.

    Args:
        service: Report service used to retrieve low-stock products.
    """
    threshold_text = _prompt_text("Low-stock threshold", "5")
    products = service.get_low_stock_products(int(threshold_text))
    if not products:
        print("No low-stock products found.")
        return
    for product in products:
        _display_product(product)


def _show_total_sales(service: ReportService) -> None:
    """Display the total sales amount.

    Args:
        service: Report service used to calculate total sales.
    """
    print(f"Total Sales: {service.get_total_sales():.2f}")


def _show_total_orders(service: ReportService) -> None:
    """Display the total order count.

    Args:
        service: Report service used to count orders.
    """
    print(f"Total Orders: {service.get_total_orders()}")


def _show_total_customers(service: ReportService) -> None:
    """Display the total customer count.

    Args:
        service: Report service used to count customers.
    """
    print(f"Total Customers: {service.get_total_customers()}")


def _show_total_invoices(service: ReportService) -> None:
    """Display the total invoice count.

    Args:
        service: Report service used to count invoices.
    """
    print(f"Total Invoices: {service.get_total_invoices()}")


def report_menu(service: ReportService) -> None:
    """Run the reports menu.

    Args:
        service: Report service used by menu actions.
    """
    actions: dict[str, Callable[[], None]] = {
        "1": lambda: _show_inventory_summary(service),
        "2": lambda: _show_low_stock_products(service),
        "3": lambda: _show_total_sales(service),
        "4": lambda: _show_total_orders(service),
        "5": lambda: _show_total_customers(service),
        "6": lambda: _show_total_invoices(service),
    }
    while True:
        _display_menu(
            "Reports",
            [
                ("1", "Inventory Summary"),
                ("2", "Low Stock Products"),
                ("3", "Total Sales"),
                ("4", "Total Orders"),
                ("5", "Total Customers"),
                ("6", "Total Invoices"),
                ("0", "Back"),
            ],
        )
        selection = _get_selection(set(actions) | {"0"})
        if selection == "0":
            return
        if selection is not None:
            _run_action(actions[selection])


def main() -> None:
    """Start the Inventory Management System command-line interface."""
    storage_service = StorageService()
    storage_service.initialize_database()

    inventory_service = InventoryService(storage_service)
    customer_service = CustomerService(storage_service)
    order_service = OrderService(storage_service)
    invoice_service = InvoiceService(storage_service)
    report_service = ReportService(storage_service)

    actions: dict[str, Callable[[], None]] = {
        "1": lambda: product_menu(inventory_service),
        "2": lambda: customer_menu(customer_service),
        "3": lambda: order_menu(order_service),
        "4": lambda: invoice_menu(invoice_service),
        "5": lambda: report_menu(report_service),
    }

    while True:
        _display_menu(
            "Inventory Management System",
            [
                ("1", "Product Management"),
                ("2", "Customer Management"),
                ("3", "Order Management"),
                ("4", "Invoice Management"),
                ("5", "Reports"),
                ("0", "Exit"),
            ],
        )
        try:
            selection = _get_selection(set(actions) | {"0"})
        except (EOFError, KeyboardInterrupt):
            print("\nThank you for using the Inventory Management System.")
            return

        if selection == "0":
            print("Thank you for using the Inventory Management System.")
            return
        if selection is not None:
            _run_action(actions[selection])


if __name__ == "__main__":
    main()
