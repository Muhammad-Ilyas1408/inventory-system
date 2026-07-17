"""Product data model for the inventory system."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, ClassVar


@dataclass
class Product:
    """Represent an item that can be tracked in inventory.

    Attributes:
        id: Unique identifier for the product.
        name: Display name of the product.
        category: Category used to organize the product.
        price: Unit price of the product.
        quantity: Number of units currently in stock.
        supplier: Name of the product supplier.
        created_at: Timestamp for when the product was created.
        updated_at: Timestamp for the most recent product update.
    """

    id: str
    name: str
    category: str
    price: float
    quantity: int
    supplier: str
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    _REQUIRED_TEXT_FIELDS: ClassVar[tuple[str, ...]] = (
        "id",
        "name",
        "category",
        "supplier",
    )

    def __post_init__(self) -> None:
        """Validate product data after initialization.

        Raises:
            ValueError: If a required field is empty or a numeric value is invalid.
        """
        for field_name in self._REQUIRED_TEXT_FIELDS:
            field_value = getattr(self, field_name)
            if not isinstance(field_value, str) or not field_value.strip():
                raise ValueError(f"Product {field_name} cannot be empty.")
            setattr(self, field_name, field_value.strip())

        if isinstance(self.price, bool) or not isinstance(self.price, (int, float)):
            raise ValueError("Product price must be a number.")
        if self.price < 0:
            raise ValueError("Product price must be greater than or equal to 0.")
        self.price = float(self.price)

        if isinstance(self.quantity, bool) or not isinstance(self.quantity, int):
            raise ValueError("Product quantity must be an integer.")
        if self.quantity < 0:
            raise ValueError("Product quantity must be greater than or equal to 0.")

        if not isinstance(self.created_at, datetime):
            raise ValueError("Product created_at must be a datetime object.")
        if not isinstance(self.updated_at, datetime):
            raise ValueError("Product updated_at must be a datetime object.")

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable representation of the product.

        Returns:
            A dictionary containing the product's data.
        """
        return {
            "id": self.id,
            "name": self.name,
            "category": self.category,
            "price": self.price,
            "quantity": self.quantity,
            "supplier": self.supplier,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Product":
        """Create a product from a dictionary representation.

        Args:
            data: Dictionary containing product data.

        Returns:
            A product initialized from the provided dictionary.
        """
        return cls(
            id=data["id"],
            name=data["name"],
            category=data["category"],
            price=data["price"],
            quantity=data["quantity"],
            supplier=data["supplier"],
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]),
        )

    def update_timestamp(self) -> None:
        """Record the current time as the product's latest update."""
        self.updated_at = datetime.now()

    def __str__(self) -> str:
        """Return a concise, human-readable product description.

        Returns:
            A formatted summary of the product.
        """
        return (
            f"Product(ID={self.id}, Name={self.name}, Price={self.price:.2f}, "
            f"Quantity={self.quantity})"
        )
