"""Display helpers for Inventory Management System models."""

from models.customer import Customer
from models.invoice import Invoice
from models.order import Order
from models.product import Product


def display_heading(title: str) -> None:
    """Display a section heading.

    Args:
        title: Text displayed in the heading.
    """
    print("\n" + "-" * 40)
    print(title)
    print("-" * 40)


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


def display_product(product: Product) -> None:
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


def display_customer(customer: Customer) -> None:
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


def display_order(order: Order) -> None:
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


def display_invoice(invoice: Invoice) -> None:
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
