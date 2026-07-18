"""JSON database initialization for the inventory system."""

import json

from config import DATABASE_PATH


class StorageService:
    """Manage persistent storage for the inventory system."""

    DEFAULT_SCHEMA: dict[str, list] = {
        "products": [],
        "customers": [],
        "orders": [],
        "invoices": [],
    }

    def initialize_database(self) -> None:
        """Create the database with the default schema when it is missing.

        Raises:
            OSError: If the database file cannot be created or written.
        """
        if DATABASE_PATH.exists():
            return

        with DATABASE_PATH.open("x", encoding="utf-8") as database_file:
            json.dump(self.DEFAULT_SCHEMA, database_file, indent=4, ensure_ascii=False)
