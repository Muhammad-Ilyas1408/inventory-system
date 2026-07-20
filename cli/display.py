"""Display helpers for Inventory Management System models."""

import re

from models.customer import Customer
from models.invoice import Invoice
from models.order import Order
from models.product import Product

DISPLAY_WIDTH = 40


def display_heading(title: str) -> None:
    """Display a section heading.

    Args:
        title: Text displayed in the heading.
    """
    print("\n" + "=" * DISPLAY_WIDTH)
    print(title)
    print("=" * DISPLAY_WIDTH)


def display_record_separator() -> None:
    """Display a separator between detailed records."""
    print("-" * DISPLAY_WIDTH)


def display_error(message: str) -> None:
    """Display a user-facing error message in a readable format.

    Args:
        message: Error text returned by the application layer.
    """
    stock_error = re.fullmatch(
        r"Insufficient stock for product '(.+)'\. Available: (\d+)\. "
        r"Requested: (\d+)\.",
        message,
    )
    if stock_error is not None:
        product_name, available, requested = stock_error.groups()
        print(f'Insufficient stock for product "{product_name}".')
        print(f"Available: {available}")
        print(f"Requested: {requested}")
        return
    print(message)


def display_customer_selection(customers: list[Customer]) -> None:
    """Display customers as numbered order-creation choices.

    Args:
        customers: Customers available for selection.
    """
    display_heading("Available Customers")
    for index, customer in enumerate(customers, start=1):
        print(f"\n{index}. {customer.id} - {customer.full_name}")


def display_product_selection(products: list[Product]) -> None:
    """Display products as numbered order-creation choices.

    Args:
        products: Products available for selection.
    """
    display_heading("Available Products")
    for index, product in enumerate(products, start=1):
        print(f"\n{index}. {product.id} - {product.name}")
        print(f"   Price: {product.price:.2f}")
        print(f"   Stock: {product.quantity}")
        if product.quantity == 0:
            print("   OUT OF STOCK")


def display_product(product: Product) -> None:
    """Display a product in a readable format.

    Args:
        product: Product to display.
    """
    display_record_separator()
    print(f"ID: {product.id}")
    print(f"Name: {product.name}")
    print(f"Category: {product.category}")
    print(f"Price: {product.price:.2f}")
    print(f"Quantity: {product.quantity}")
    print(f"Supplier: {product.supplier}")


def display_customer(customer: Customer) -> None:
    """Display a customer in a readable format.

    Args:
        customer: Customer to display.
    """
    display_record_separator()
    print(f"ID: {customer.id}")
    print(f"Name: {customer.full_name}")
    print(f"Email: {customer.email}")
    print(f"Phone: {customer.phone}")
    print(f"Address: {customer.address}")


def display_order(order: Order) -> None:
    """Display an order in a readable format.

    Args:
        order: Order to display.
    """
    display_record_separator()
    print(f"ID: {order.id}")
    print(f"Customer ID: {order.customer_id}")
    print(f"Status: {order.status.value}")
    print(f"Total: {order.total:.2f}")
    for item in order.items:
        print(f"  - {item.product_name}: {item.quantity} x {item.unit_price:.2f}")


def display_invoice(invoice: Invoice) -> None:
    """Display an invoice in a readable format.

    Args:
        invoice: Invoice to display.
    """
    display_record_separator()
    print(f"ID: {invoice.id}")
    print(f"Order ID: {invoice.order_id}")
    print(f"Customer: {invoice.customer_name}")
    print(f"Email: {invoice.customer_email}")
    print(f"Subtotal: {invoice.subtotal:.2f}")
    print(f"Total: {invoice.total:.2f}")
    print(f"Issued At: {invoice.issued_at.isoformat(sep=' ', timespec='seconds')}")


def display_order_confirmation(
    order: Order,
    customer: Customer,
    invoice: Invoice,
) -> None:
    """Display a concise confirmation for a newly created order.

    Args:
        order: Newly created order.
        customer: Customer associated with the order.
        invoice: Automatically generated invoice for the order.
    """
    display_heading("Order Created Successfully")
    print("\nOrder ID:")
    print(order.id)
    print("\nCustomer:")
    print(customer.full_name)
    print("\nItems:")
    for item in order.items:
        print(f"• {item.product_name} ×{item.quantity}")
    print("\nOrder Total:")
    print(f"{invoice.total:.2f}")
    print("\nInvoice:")
    print(f"{invoice.id} generated successfully.")
