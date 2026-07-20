"""Application startup and main-menu presentation logic."""

from collections.abc import Callable

from cli.customer_menu import customer_menu
from cli.invoice_menu import invoice_menu
from cli.menu import display_menu, get_selection, run_action
from cli.order_menu import order_menu
from cli.product_menu import product_menu
from cli.report_menu import report_menu
from services.customer_service import CustomerService
from services.inventory_service import InventoryService
from services.invoice_service import InvoiceService
from services.order_service import OrderService
from services.report_service import ReportService
from services.storage_service import StorageService


def run() -> None:
    """Start the Inventory Management System command-line interface."""
    storage_service = StorageService()
    storage_service.initialize_database()

    inventory_service = InventoryService(storage_service)
    customer_service = CustomerService(storage_service)
    invoice_service = InvoiceService(storage_service)
    order_service = OrderService(
        storage_service,
        inventory_service,
        invoice_service,
    )
    report_service = ReportService(storage_service)

    actions: dict[str, Callable[[], None]] = {
        "1": lambda: product_menu(inventory_service),
        "2": lambda: customer_menu(customer_service),
        "3": lambda: order_menu(
            order_service,
            customer_service,
            inventory_service,
        ),
        "4": lambda: invoice_menu(invoice_service),
        "5": lambda: report_menu(report_service),
    }

    while True:
        display_menu(
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
            selection = get_selection(set(actions) | {"0"})
        except (EOFError, KeyboardInterrupt):
            print("\nThank you for using the Inventory Management System.")
            return

        if selection == "0":
            print("Thank you for using the Inventory Management System.")
            return
        if selection is not None:
            run_action(actions[selection])
