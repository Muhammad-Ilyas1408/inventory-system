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

    def _validate_schema(self, data: dict[str, list]) -> None:
        """Validate the Version 1 database schema.

        Args:
            data: Database data to validate.

        Raises:
            ValueError: If the database schema is invalid.
        """
        if not isinstance(data, dict):
            raise ValueError(
                "Invalid database schema: top-level JSON object must be a dictionary."
            )

        expected_keys = set(self.DEFAULT_SCHEMA.keys())
        if set(data.keys()) != expected_keys:
            raise ValueError(
                "Invalid database schema: unexpected or missing top-level collections."
            )

        if any(not isinstance(data[collection], list) for collection in expected_keys):
            raise ValueError("Invalid database schema: all collections must be lists.")

    def initialize_database(self) -> None:
        """Create the database with the default schema when it is missing.

        Raises:
            OSError: If the database file cannot be created or written.
        """
        if DATABASE_PATH.exists():
            return

        with DATABASE_PATH.open("x", encoding="utf-8") as database_file:
            json.dump(self.DEFAULT_SCHEMA, database_file, indent=4, ensure_ascii=False)

    def load_data(self) -> dict[str, list]:
        """Load and validate the complete database.

        Returns:
            dict[str, list]: The validated database data.

        Raises:
            json.JSONDecodeError: If the database contains invalid JSON.
            ValueError: If the database schema is invalid.
            OSError: If the database cannot be opened or read.
        """
        if not DATABASE_PATH.exists():
            self.initialize_database()

        with DATABASE_PATH.open("r", encoding="utf-8") as database_file:
            data = json.load(database_file)

        self._validate_schema(data)

        return data

    def save_data(self, data: dict[str, list]) -> None:
        """Validate and save the complete database.

        Args:
            data: Database data to save.

        Raises:
            TypeError: If the data cannot be serialized as JSON.
            ValueError: If the database schema is invalid.
            OSError: If the database cannot be created or written.
        """
        self._validate_schema(data)

        if not DATABASE_PATH.exists():
            self.initialize_database()

        with DATABASE_PATH.open("w", encoding="utf-8") as database_file:
            json.dump(
                data,
                database_file,
                indent=4,
                ensure_ascii=False,
            )
