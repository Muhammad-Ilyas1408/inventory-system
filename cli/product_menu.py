"""Product-management presentation logic."""

from collections.abc import Callable

from cli.display import display_product
from cli.input_helpers import prompt_text
from cli.menu import display_menu, get_selection, run_action
from models.product import Product
from services.inventory_service import InventoryService


def add_product(service: InventoryService) -> None:
    """Collect and add a product through InventoryService.

    Args:
        service: Inventory service used to add the product.
    """
    product = Product(
        id=prompt_text("ID"),
        name=prompt_text("Name"),
        category=prompt_text("Category"),
        price=float(prompt_text("Price")),
        quantity=int(prompt_text("Quantity")),
        supplier=prompt_text("Supplier"),
    )
    service.add_product(product)
    print("Product added successfully.")


def view_products(service: InventoryService) -> None:
    """Display all products through InventoryService.

    Args:
        service: Inventory service used to retrieve products.
    """
    products = service.get_all_products()
    if not products:
        print("No products found.")
        return
    for product in products:
        display_product(product)


def search_products(service: InventoryService) -> None:
    """Search and display products.

    Args:
        service: Inventory service used to search products.
    """
    products = service.search_products(prompt_text("Search keyword"))
    if not products:
        print("No matching products found.")
        return
    for product in products:
        display_product(product)


def update_product(service: InventoryService) -> None:
    """Collect and update an existing product.

    Args:
        service: Inventory service used to update the product.
    """
    product_id = prompt_text("Product ID")
    existing = service.get_product_by_id(product_id)
    if existing is None:
        print("Product not found.")
        return
    product = Product(
        id=existing.id,
        name=prompt_text("Name", existing.name),
        category=prompt_text("Category", existing.category),
        price=float(prompt_text("Price", str(existing.price))),
        quantity=int(prompt_text("Quantity", str(existing.quantity))),
        supplier=prompt_text("Supplier", existing.supplier),
        created_at=existing.created_at,
        updated_at=existing.updated_at,
    )
    service.update_product(product)
    print("Product updated successfully.")


def delete_product(service: InventoryService) -> None:
    """Delete a product through InventoryService.

    Args:
        service: Inventory service used to delete the product.
    """
    service.delete_product(prompt_text("Product ID"))
    print("Product deleted successfully.")


def product_menu(service: InventoryService) -> None:
    """Run the product management menu.

    Args:
        service: Inventory service used by menu actions.
    """
    actions: dict[str, Callable[[], None]] = {
        "1": lambda: add_product(service),
        "2": lambda: view_products(service),
        "3": lambda: search_products(service),
        "4": lambda: update_product(service),
        "5": lambda: delete_product(service),
    }
    while True:
        display_menu(
            "Product Management",
            [
                ("1", "Add Product"),
                ("2", "View All Products"),
                ("3", "Search Product"),
                ("4", "Update Product"),
                ("5", "Delete Product"),
                ("0", "Back"),
            ],
        )
        selection = get_selection(set(actions) | {"0"})
        if selection == "0":
            return
        if selection is not None:
            run_action(actions[selection])
