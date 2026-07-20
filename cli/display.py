"""Display helpers for Inventory Management System models."""

from models.customer import Customer
from models.invoice import Invoice
from models.order import Order
from models.product import Product


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
