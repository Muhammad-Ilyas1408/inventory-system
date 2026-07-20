"""Invoice-management presentation logic."""

from collections.abc import Callable
from datetime import datetime

from cli.display import display_invoice
from cli.input_helpers import prompt_order_items, prompt_text
from cli.menu import display_menu, get_selection, run_action
from models.invoice import Invoice
from services.invoice_service import InvoiceService


def create_invoice(service: InvoiceService) -> None:
    """Collect and create an invoice through InvoiceService.

    Args:
        service: Invoice service used to create the invoice.
    """
    issued_at_text = prompt_text("Issued At (ISO format, blank for now)", "")
    issued_at = (
        datetime.fromisoformat(issued_at_text)
        if issued_at_text
        else datetime.now()
    )
    invoice = Invoice(
        id=prompt_text("Invoice ID"),
        order_id=prompt_text("Order ID"),
        customer_name=prompt_text("Customer Name"),
        customer_email=prompt_text("Customer Email"),
        items=prompt_order_items(),
        subtotal=float(prompt_text("Subtotal")),
        total=float(prompt_text("Total")),
        issued_at=issued_at,
    )
    service.create_invoice(invoice)
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
