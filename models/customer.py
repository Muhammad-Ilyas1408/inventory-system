"""Customer data model for the inventory system."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, ClassVar


@dataclass
class Customer:
    """Represent a customer who can place orders.

    Attributes:
        id: Unique identifier for the customer.
        first_name: Customer's first name.
        last_name: Customer's last name.
        email: Customer's email address.
        phone: Customer's phone number.
        address: Customer's address.
        created_at: Timestamp for when the customer was created.
        updated_at: Timestamp for the most recent customer update.
    """

    id: str
    first_name: str
    last_name: str
    email: str
    phone: str
    address: str
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    _REQUIRED_TEXT_FIELDS: ClassVar[tuple[str, ...]] = (
        "id",
        "first_name",
        "last_name",
        "email",
        "phone",
        "address",
    )

    def __post_init__(self) -> None:
        """Validate customer data after initialization.

        Raises:
            ValueError: If a required field is empty or a timestamp is invalid.
        """
        for field_name in self._REQUIRED_TEXT_FIELDS:
            field_value = getattr(self, field_name)
            if not isinstance(field_value, str) or not field_value.strip():
                raise ValueError(f"Customer {field_name} cannot be empty.")
            setattr(self, field_name, field_value.strip())

        if not isinstance(self.created_at, datetime):
            raise ValueError("Customer created_at must be a datetime object.")
        if not isinstance(self.updated_at, datetime):
            raise ValueError("Customer updated_at must be a datetime object.")

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable representation of the customer.

        Returns:
            A dictionary containing the customer's data.
        """
        return {
            "id": self.id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "email": self.email,
            "phone": self.phone,
            "address": self.address,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Customer":
        """Create a customer from a dictionary representation.

        Args:
            data: Dictionary containing customer data.

        Returns:
            A customer initialized from the provided dictionary.
        """
        return cls(
            id=data["id"],
            first_name=data["first_name"],
            last_name=data["last_name"],
            email=data["email"],
            phone=data["phone"],
            address=data["address"],
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]),
        )

    def update_timestamp(self) -> None:
        """Record the current time as the customer's latest update."""
        self.updated_at = datetime.now()

    @property
    def full_name(self) -> str:
        """Return the customer's full name.

        Returns:
            The customer's first and last names separated by a space.
        """
        return f"{self.first_name} {self.last_name}"

    def __str__(self) -> str:
        """Return a concise, human-readable customer description.

        Returns:
            A formatted summary of the customer.
        """
        return f"Customer(ID={self.id}, Name={self.full_name})"
