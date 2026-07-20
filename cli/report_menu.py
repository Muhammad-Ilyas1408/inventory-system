"""Report presentation logic."""

from collections.abc import Callable

from cli.display import display_product
from cli.input_helpers import prompt_text
from cli.menu import display_menu, get_selection, run_action
from services.report_service import ReportService


def show_inventory_summary(service: ReportService) -> None:
    """Display the inventory summary.

    Args:
        service: Report service used to retrieve the summary.
    """
    summary = service.get_inventory_summary()
    print(f"Total Products: {summary['total_products']}")
    print(f"Total Stock: {summary['total_stock']}")


def show_low_stock_products(service: ReportService) -> None:
    """Display products at or below a chosen stock threshold.

    Args:
        service: Report service used to retrieve low-stock products.
    """
    threshold_text = prompt_text("Low-stock threshold", "5")
    products = service.get_low_stock_products(int(threshold_text))
    if not products:
        print("No low-stock products found.")
        return
    for product in products:
        display_product(product)


def show_total_sales(service: ReportService) -> None:
    """Display the total sales amount.

    Args:
        service: Report service used to calculate total sales.
    """
    print(f"Total Sales: {service.get_total_sales():.2f}")


def show_total_orders(service: ReportService) -> None:
    """Display the total order count.

    Args:
        service: Report service used to count orders.
    """
    print(f"Total Orders: {service.get_total_orders()}")


def show_total_customers(service: ReportService) -> None:
    """Display the total customer count.

    Args:
        service: Report service used to count customers.
    """
    print(f"Total Customers: {service.get_total_customers()}")


def show_total_invoices(service: ReportService) -> None:
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
        "1": lambda: show_inventory_summary(service),
        "2": lambda: show_low_stock_products(service),
        "3": lambda: show_total_sales(service),
        "4": lambda: show_total_orders(service),
        "5": lambda: show_total_customers(service),
        "6": lambda: show_total_invoices(service),
    }
    while True:
        display_menu(
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
        selection = get_selection(set(actions) | {"0"})
        if selection == "0":
            return
        if selection is not None:
            run_action(actions[selection])
