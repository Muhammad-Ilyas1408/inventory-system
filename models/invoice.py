"""Invoice data model for the inventory system."""

from dataclasses import dataclass
from datetime import datetime
from typing import Any, ClassVar

from models.order_item import OrderItem


@dataclass
class Invoice:
    """Represent a historical financial record for a completed order.

    Attributes:
        id: Unique identifier for the invoice.
        order_id: Identifier of the completed order.
        customer_name: Customer name recorded when the invoice was created.
        customer_email: Customer email recorded when the invoice was created.
        items: Purchased product snapshots recorded on the invoice.
        subtotal: Stored subtotal of the completed purchase.
        total: Stored total of the completed purchase.
        issued_at: Timestamp for when the invoice was issued.
    """

    id: str
    order_id: str
    customer_name: str
    customer_email: str
    items: list[OrderItem]
    subtotal: float
    total: float
    issued_at: datetime

    _REQUIRED_TEXT_FIELDS: ClassVar[tuple[str, ...]] = (
        "id",
        "order_id",
        "customer_name",
        "customer_email",
    )

    def __post_init__(self) -> None:
        """Validate invoice data after initialization.

        Raises:
            ValueError: If an invoice field contains an invalid value.
        """
        for field_name in self._REQUIRED_TEXT_FIELDS:
            field_value = getattr(self, field_name)
            if not isinstance(field_value, str) or not field_value.strip():
                raise ValueError(f"Invoice {field_name} cannot be empty.")
            setattr(self, field_name, field_value.strip())

        if not isinstance(self.items, list):
            raise ValueError("Invoice items must be a list.")
        if not self.items:
            raise ValueError("Invoice items cannot be empty.")
        if not all(isinstance(item, OrderItem) for item in self.items):
            raise ValueError("Every invoice item must be an OrderItem instance.")

        if isinstance(self.subtotal, bool) or not isinstance(
            self.subtotal, (int, float)
        ):
            raise ValueError("Invoice subtotal must be a number.")
        if self.subtotal < 0:
            raise ValueError("Invoice subtotal must be greater than or equal to 0.")
        self.subtotal = float(self.subtotal)

        if isinstance(self.total, bool) or not isinstance(self.total, (int, float)):
            raise ValueError("Invoice total must be a number.")
        if self.total < 0:
            raise ValueError("Invoice total must be greater than or equal to 0.")
        self.total = float(self.total)

        if not isinstance(self.issued_at, datetime):
            raise ValueError("Invoice issued_at must be a datetime object.")

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable representation of the invoice.

        Returns:
            A dictionary containing the invoice's data.
        """
        return {
            "id": self.id,
            "order_id": self.order_id,
            "customer_name": self.customer_name,
            "customer_email": self.customer_email,
            "items": [item.to_dict() for item in self.items],
            "subtotal": self.subtotal,
            "total": self.total,
            "issued_at": self.issued_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Invoice":
        """Create an invoice from a dictionary representation.

        Args:
            data: Dictionary containing invoice data.

        Returns:
            An invoice initialized from the provided dictionary.
        """
        return cls(
            id=data["id"],
            order_id=data["order_id"],
            customer_name=data["customer_name"],
            customer_email=data["customer_email"],
            items=[OrderItem.from_dict(item) for item in data["items"]],
            subtotal=data["subtotal"],
            total=data["total"],
            issued_at=datetime.fromisoformat(data["issued_at"]),
        )

    def __str__(self) -> str:
        """Return a concise, human-readable invoice description.

        Returns:
            A formatted summary of the invoice.
        """
        return (
            f"Invoice(ID={self.id}, Order={self.order_id}, "
            f"Customer={self.customer_name}, Items={len(self.items)}, "
            f"Total={self.total:.2f})"
        )
