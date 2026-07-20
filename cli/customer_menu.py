"""Customer-management presentation logic."""

from collections.abc import Callable

from cli.display import display_customer
from cli.input_helpers import prompt_text
from cli.menu import display_menu, get_selection, run_action
from models.customer import Customer
from services.customer_service import CustomerService


def add_customer(service: CustomerService) -> None:
    """Collect and add a customer through CustomerService.

    Args:
        service: Customer service used to add the customer.
    """
    customer = Customer(
        id=prompt_text("ID"),
        first_name=prompt_text("First Name"),
        last_name=prompt_text("Last Name"),
        email=prompt_text("Email"),
        phone=prompt_text("Phone"),
        address=prompt_text("Address"),
    )
    service.add_customer(customer)
    print("Customer added successfully.")


def view_customers(service: CustomerService) -> None:
    """Display all customers through CustomerService.

    Args:
        service: Customer service used to retrieve customers.
    """
    customers = service.get_all_customers()
    if not customers:
        print("No customers found.")
        return
    for customer in customers:
        display_customer(customer)


def search_customers(service: CustomerService) -> None:
    """Search and display customers.

    Args:
        service: Customer service used to search customers.
    """
    customers = service.search_customers(prompt_text("Search keyword"))
    if not customers:
        print("No matching customers found.")
        return
    for customer in customers:
        display_customer(customer)


def update_customer(service: CustomerService) -> None:
    """Collect and update an existing customer.

    Args:
        service: Customer service used to update the customer.
    """
    customer_id = prompt_text("Customer ID")
    existing = service.get_customer_by_id(customer_id)
    if existing is None:
        print("Customer not found.")
        return
    customer = Customer(
        id=existing.id,
        first_name=prompt_text("First Name", existing.first_name),
        last_name=prompt_text("Last Name", existing.last_name),
        email=prompt_text("Email", existing.email),
        phone=prompt_text("Phone", existing.phone),
        address=prompt_text("Address", existing.address),
        created_at=existing.created_at,
        updated_at=existing.updated_at,
    )
    service.update_customer(customer)
    print("Customer updated successfully.")


def delete_customer(service: CustomerService) -> None:
    """Delete a customer through CustomerService.

    Args:
        service: Customer service used to delete the customer.
    """
    service.delete_customer(prompt_text("Customer ID"))
    print("Customer deleted successfully.")


def customer_menu(service: CustomerService) -> None:
    """Run the customer management menu.

    Args:
        service: Customer service used by menu actions.
    """
    actions: dict[str, Callable[[], None]] = {
        "1": lambda: add_customer(service),
        "2": lambda: view_customers(service),
        "3": lambda: search_customers(service),
        "4": lambda: update_customer(service),
        "5": lambda: delete_customer(service),
    }
    while True:
        display_menu(
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
        selection = get_selection(set(actions) | {"0"})
        if selection == "0":
            return
        if selection is not None:
            run_action(actions[selection])
