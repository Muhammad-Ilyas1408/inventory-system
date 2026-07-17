"""Shared enumeration types for the inventory system."""

from enum import Enum


class OrderStatus(Enum):
    """Represent the lifecycle status of an order."""

    PENDING = "PENDING"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"
