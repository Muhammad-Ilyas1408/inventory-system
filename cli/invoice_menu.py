"""Invoice-management presentation logic."""

from collections.abc import Callable

from cli.display import display_error, display_heading, display_invoice
from cli.input_helpers import prompt_text
from cli.menu import display_menu, get_selection, run_action
from services.invoice_service import InvoiceService


def create_invoice(service: InvoiceService) -> None:
    """Collect and create an invoice through InvoiceService.

    Args:
        service: Invoice service used to create the invoice.
    """
    invoice_id = prompt_text("Invoice ID")
    order_id = prompt_text("Order ID")
    try:
        service.create_invoice_for_order(invoice_id, order_id)
    except ValueError as error:
        display_error(str(error))
        return
    print("Invoice created successfully.")


def view_invoices(service: InvoiceService) -> None:
    """Display all invoices through InvoiceService.

    Args:
        service: Invoice service used to retrieve invoices.
    """
    invoices = service.get_all_invoices()
    if not invoices:
        print("No invoices found.")
        return
    display_heading("Invoices")
    for invoice in invoices:
        display_invoice(invoice)


def search_invoices(service: InvoiceService) -> None:
    """Search and display invoices.

    Args:
        service: Invoice service used to search invoices.
    """
    invoices = service.search_invoices(prompt_text("Search keyword"))
    if not invoices:
        print("No matching invoices found.")
        return
    display_heading("Invoices")
    for invoice in invoices:
        display_invoice(invoice)


def view_invoice_by_order(service: InvoiceService) -> None:
    """Display an invoice for a selected order.

    Args:
        service: Invoice service used to retrieve the invoice.
    """
    invoice = service.get_invoice_by_order(prompt_text("Order ID"))
    if invoice is None:
        print("No invoice found for this order.")
        return
    display_heading("Invoices")
    display_invoice(invoice)


def view_customer_invoices(service: InvoiceService) -> None:
    """Display invoices associated with a customer.

    Args:
        service: Invoice service used to retrieve customer invoices.
    """
    invoices = service.get_invoices_by_customer(prompt_text("Customer ID"))
    if not invoices:
        print("No invoices found for this customer.")
        return
    display_heading("Invoices")
    for invoice in invoices:
        display_invoice(invoice)


def delete_invoice(service: InvoiceService) -> None:
    """Delete an invoice through InvoiceService.

    Args:
        service: Invoice service used to delete the invoice.
    """
    service.delete_invoice(prompt_text("Invoice ID"))
    print("Invoice deleted successfully.")


def invoice_menu(service: InvoiceService) -> None:
    """Run the invoice management menu.

    Args:
        service: Invoice service used by menu actions.
    """
    actions: dict[str, Callable[[], None]] = {
        "1": lambda: create_invoice(service),
        "2": lambda: view_invoices(service),
        "3": lambda: search_invoices(service),
        "4": lambda: view_invoice_by_order(service),
        "5": lambda: view_customer_invoices(service),
        "6": lambda: delete_invoice(service),
    }
    while True:
        display_menu(
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
        selection = get_selection(set(actions) | {"0"})
        if selection == "0":
            return
        if selection is not None:
            run_action(actions[selection])
