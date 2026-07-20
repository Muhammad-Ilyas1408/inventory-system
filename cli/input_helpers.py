"""Input collection helpers for the command-line interface."""

from models.order_item import OrderItem


def prompt_text(label: str, default: str | None = None) -> str:
    """Prompt for text, optionally using a displayed default value.

    Args:
        label: Description of the requested value.
        default: Value returned when the user submits blank input.

    Returns:
        The entered text or the provided default.
    """
    prompt = f"{label}"
    if default is not None:
        prompt += f" [{default}]"
    value = input(f"{prompt}: ").strip()
    return value if value or default is None else default


def prompt_order_items() -> list[OrderItem]:
    """Collect one or more order items from the user.

    Returns:
        Order items entered by the user.
    """
    items: list[OrderItem] = []
    while True:
        print("\nOrder Item")
        items.append(
            OrderItem(
                product_id=prompt_text("Product ID"),
                product_name=prompt_text("Product Name"),
                unit_price=float(prompt_text("Unit Price")),
                quantity=int(prompt_text("Quantity")),
            )
        )
        if prompt_text("Add another item? (y/n)", "n").casefold() != "y":
            return items
