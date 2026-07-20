"""Order-management presentation logic."""

from collections.abc import Callable

from cli.display import (
    display_customer_selection,
    display_order,
    display_product_selection,
)
from cli.input_helpers import prompt_text
from cli.menu import display_menu, get_selection, run_action
from models.customer import Customer
from models.enums import OrderStatus
from models.order import Order
from models.order_item import OrderItem
from models.product import Product
from services.customer_service import CustomerService
from services.inventory_service import InventoryService
from services.order_service import OrderService


def select_customer(service: CustomerService) -> Customer | None:
    """Display customers and return the selected customer.

    Args:
        service: Customer service used to retrieve customers.

    Returns:
        The selected customer, or None when no selection can be made.
    """
    customers = service.get_all_customers()
    if not customers:
        print("No customers found. Order creation cancelled.")
        return None
    display_customer_selection(customers)
    selection = get_selection(
        {str(index) for index in range(1, len(customers) + 1)},
        "Select customer: ",
    )
    if selection is None:
        return None
    return customers[int(selection) - 1]


def select_product(service: InventoryService) -> Product | None:
    """Display products and return the selected product.

    Args:
        service: Inventory service used to retrieve products.

    Returns:
        The selected product, or None when no selection can be made.
    """
    products = service.get_all_products()
    if not products:
        print("No products found. Order creation cancelled.")
        return None
    display_product_selection(products)
    selection = get_selection(
        {str(index) for index in range(1, len(products) + 1)},
        "Select product: ",
    )
    if selection is None:
        return None
    return products[int(selection) - 1]


def prompt_selected_order_items(
    service: InventoryService,
) -> list[OrderItem] | None:
    """Collect order items using existing product records.

    Args:
        service: Inventory service used to retrieve products.

    Returns:
        Selected order items, or None when item collection is cancelled.
    """
    items: list[OrderItem] = []
    while True:
        print("\nOrder Item")
        product = select_product(service)
        if product is None:
            return None
        items.append(
            OrderItem(
                product_id=product.id,
                product_name=product.name,
                unit_price=product.price,
                quantity=int(prompt_text("Quantity")),
            )
        )
        if prompt_text("Add another item? (y/n)", "n").casefold() != "y":
            return items


def create_order(
    service: OrderService,
    customer_service: CustomerService,
    inventory_service: InventoryService,
) -> None:
    """Collect and create an order through OrderService.

    Args:
        service: Order service used to create the order.
        customer_service: Customer service used to select a customer.
        inventory_service: Inventory service used to select products.
    """
    order_id = prompt_text("Order ID")
    customer = select_customer(customer_service)
    if customer is None:
        return
    items = prompt_selected_order_items(inventory_service)
    if items is None:
        return
    order = Order(
        id=order_id,
        customer_id=customer.id,
        items=items,
        status=OrderStatus.PENDING,
    )
    service.create_order(order)
    print("Order created successfully.")
    print("Invoice generated successfully.")


def view_orders(service: OrderService) -> None:
    """Display all orders through OrderService.

    Args:
        service: Order service used to retrieve orders.
    """
    orders = service.get_all_orders()
    if not orders:
        print("No orders found.")
        return
    for order in orders:
        display_order(order)


def search_orders(service: OrderService) -> None:
    """Search and display orders.

    Args:
        service: Order service used to search orders.
    """
    orders = service.search_orders(prompt_text("Search keyword"))
    if not orders:
        print("No matching orders found.")
        return
    for order in orders:
        display_order(order)


def view_customer_orders(service: OrderService) -> None:
    """Display all orders for a customer.

    Args:
        service: Order service used to retrieve customer orders.
    """
    orders = service.get_orders_by_customer(prompt_text("Customer ID"))
    if not orders:
        print("No orders found for this customer.")
        return
    for order in orders:
        display_order(order)


def delete_order(service: OrderService) -> None:
    """Delete an order through OrderService.

    Args:
        service: Order service used to delete the order.
    """
    service.delete_order(prompt_text("Order ID"))
    print("Order deleted successfully.")


def calculate_order_total(service: OrderService) -> None:
    """Calculate and display an order total.

    Args:
        service: Order service used to calculate the total.
    """
    total = service.calculate_order_total(prompt_text("Order ID"))
    print(f"Order total: {total:.2f}")


def order_menu(
    service: OrderService,
    customer_service: CustomerService,
    inventory_service: InventoryService,
) -> None:
    """Run the order management menu.

    Args:
        service: Order service used by menu actions.
        customer_service: Customer service used by order creation.
        inventory_service: Inventory service used by order creation.
    """
    actions: dict[str, Callable[[], None]] = {
        "1": lambda: create_order(service, customer_service, inventory_service),
        "2": lambda: view_orders(service),
        "3": lambda: search_orders(service),
        "4": lambda: view_customer_orders(service),
        "5": lambda: delete_order(service),
        "6": lambda: calculate_order_total(service),
    }
    while True:
        display_menu(
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
        selection = get_selection(set(actions) | {"0"})
        if selection == "0":
            return
        if selection is not None:
            run_action(actions[selection])
