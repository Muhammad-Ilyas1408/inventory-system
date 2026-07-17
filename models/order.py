"""Order data model for the inventory system."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, ClassVar

from models.enums import OrderStatus
from models.order_item import OrderItem


@dataclass
class Order:
    """Represent a customer's purchase.

    Attributes:
        id: Unique identifier for the order.
        customer_id: Identifier of the customer who placed the order.
        items: Purchased product snapshots in the order.
        status: Current status of the order.
        created_at: Timestamp for when the order was created.
        updated_at: Timestamp for the most recent order update.
    """

    id: str
    customer_id: str
    items: list[OrderItem]
    status: OrderStatus = OrderStatus.PENDING
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    _REQUIRED_TEXT_FIELDS: ClassVar[tuple[str, ...]] = ("id", "customer_id")

    def __post_init__(self) -> None:
        """Validate order data after initialization.

        Raises:
            ValueError: If an order field contains an invalid value.
        """
        for field_name in self._REQUIRED_TEXT_FIELDS:
            field_value = getattr(self, field_name)
            if not isinstance(field_value, str) or not field_value.strip():
                raise ValueError(f"Order {field_name} cannot be empty.")
            setattr(self, field_name, field_value.strip())

        if not isinstance(self.items, list):
            raise ValueError("Order items must be a list.")
        if not self.items:
            raise ValueError("Order items cannot be empty.")
        if not all(isinstance(item, OrderItem) for item in self.items):
            raise ValueError("Every order item must be an OrderItem instance.")

        if not isinstance(self.status, OrderStatus):
            raise ValueError("Order status must be an OrderStatus enum.")
        if not isinstance(self.created_at, datetime):
            raise ValueError("Order created_at must be a datetime object.")
        if not isinstance(self.updated_at, datetime):
            raise ValueError("Order updated_at must be a datetime object.")

    @property
    def total(self) -> float:
        """Return the order's unrounded total purchase price.

        Returns:
            The sum of all order item subtotals.
        """
        return sum(item.subtotal for item in self.items)

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable representation of the order.

        Returns:
            A dictionary containing the order's data.
        """
        return {
            "id": self.id,
            "customer_id": self.customer_id,
            "items": [item.to_dict() for item in self.items],
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Order":
        """Create an order from a dictionary representation.

        Args:
            data: Dictionary containing order data.

        Returns:
            An order initialized from the provided dictionary.
        """
        return cls(
            id=data["id"],
            customer_id=data["customer_id"],
            items=[OrderItem.from_dict(item) for item in data["items"]],
            status=OrderStatus(data["status"]),
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]),
        )

    def update_timestamp(self) -> None:
        """Record the current time as the order's latest update."""
        self.updated_at = datetime.now()

    def __str__(self) -> str:
        """Return a concise, human-readable order description.

        Returns:
            A formatted summary of the order.
        """
        return (
            f"Order(ID={self.id}, Customer={self.customer_id}, "
            f"Items={len(self.items)}, Status={self.status.value}, "
            f"Total={self.total:.2f})"
        )
