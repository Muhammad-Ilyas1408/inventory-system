"""Order item data model for the inventory system."""

from dataclasses import dataclass
from typing import Any, ClassVar


@dataclass
class OrderItem:
    """Represent a purchased product snapshot within an order.

    Attributes:
        product_id: Identifier of the purchased product.
        product_name: Name of the product at the time of purchase.
        unit_price: Price per unit at the time of purchase.
        quantity: Number of purchased units.
    """

    product_id: str
    product_name: str
    unit_price: float
    quantity: int

    _REQUIRED_TEXT_FIELDS: ClassVar[tuple[str, ...]] = (
        "product_id",
        "product_name",
    )

    def __post_init__(self) -> None:
        """Validate order item data after initialization.

        Raises:
            ValueError: If a required field is empty or a numeric value is invalid.
        """
        for field_name in self._REQUIRED_TEXT_FIELDS:
            field_value = getattr(self, field_name)
            if not isinstance(field_value, str) or not field_value.strip():
                raise ValueError(f"Order item {field_name} cannot be empty.")
            setattr(self, field_name, field_value.strip())

        if isinstance(self.unit_price, bool) or not isinstance(
            self.unit_price, (int, float)
        ):
            raise ValueError("Order item unit_price must be a number.")
        if self.unit_price < 0:
            raise ValueError(
                "Order item unit_price must be greater than or equal to 0."
            )
        self.unit_price = float(self.unit_price)

        if isinstance(self.quantity, bool) or not isinstance(self.quantity, int):
            raise ValueError("Order item quantity must be an integer.")
        if self.quantity <= 0:
            raise ValueError("Order item quantity must be greater than 0.")

    @property
    def subtotal(self) -> float:
        """Return the item's unrounded total purchase price.

        Returns:
            The unit price multiplied by the quantity.
        """
        return self.unit_price * self.quantity

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable representation of the order item.

        Returns:
            A dictionary containing the order item's data.
        """
        return {
            "product_id": self.product_id,
            "product_name": self.product_name,
            "unit_price": self.unit_price,
            "quantity": self.quantity,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "OrderItem":
        """Create an order item from a dictionary representation.

        Args:
            data: Dictionary containing order item data.

        Returns:
            An order item initialized from the provided dictionary.
        """
        return cls(
            product_id=data["product_id"],
            product_name=data["product_name"],
            unit_price=data["unit_price"],
            quantity=data["quantity"],
        )

    def __str__(self) -> str:
        """Return a concise, human-readable order item description.

        Returns:
            A formatted summary of the order item.
        """
        return (
            f"OrderItem(Product={self.product_name}, Quantity={self.quantity}, "
            f"UnitPrice={self.unit_price:.2f})"
        )
