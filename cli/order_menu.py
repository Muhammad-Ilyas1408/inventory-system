"""Order-management presentation logic."""

from collections.abc import Callable

from cli.display import display_order
from cli.input_helpers import prompt_order_items, prompt_text
from cli.menu import display_menu, get_selection, run_action
from models.enums import OrderStatus
from models.order import Order
from services.order_service import OrderService


def create_order(service: OrderService) -> None:
    """Collect and create an order through OrderService.

    Args:
        service: Order service used to create the order.
    """
    status = OrderStatus(prompt_text("Status", OrderStatus.PENDING.value).upper())
    order = Order(
        id=prompt_text("Order ID"),
        customer_id=prompt_text("Customer ID"),
        items=prompt_order_items(),
        status=status,
    )
    service.create_order(order)
    print("Order created successfully.")


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


def order_menu(service: OrderService) -> None:
    """Run the order management menu.

    Args:
        service: Order service used by menu actions.
    """
    actions: dict[str, Callable[[], None]] = {
        "1": lambda: create_order(service),
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
