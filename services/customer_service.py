"""Customer business service for customer-related operations."""

from models.customer import Customer
from services.storage_service import StorageService


class CustomerService:
    """Coordinate customer-related business operations."""

    def __init__(self, storage_service: StorageService) -> None:
        """Initialize the service with its persistence dependency.

        Args:
            storage_service: Service used to persist customer data.

        Raises:
            TypeError: If storage_service is not a StorageService instance.
        """
        if not isinstance(storage_service, StorageService):
            raise TypeError(
                "storage_service must be a StorageService instance, "
                f"got {type(storage_service).__name__}."
            )

        self._storage_service = storage_service

    def add_customer(self, customer: Customer) -> None:
        """Add a customer to the system.

        Args:
            customer: Customer to add.

        Raises:
            TypeError: If customer is not a Customer instance.
            ValueError: If a customer with the same identifier already exists.
        """
        if not isinstance(customer, Customer):
            raise TypeError("customer must be an instance of Customer.")

        data = self._storage_service.load_data()
        customers = data["customers"]

        if any(
            existing_customer.get("id") == customer.id
            for existing_customer in customers
        ):
            raise ValueError(f"Customer with ID '{customer.id}' already exists.")

        customers.append(customer.to_dict())
        self._storage_service.save_data(data)

    def get_customer_by_id(self, customer_id: str) -> Customer | None:
        """Retrieve a customer by its unique identifier.

        Args:
            customer_id: Unique identifier of the customer to retrieve.

        Returns:
            The matching customer, or None when no customer has the identifier.

        Raises:
            TypeError: If customer_id is not a string.
            ValueError: If customer_id is empty after stripping whitespace.
        """
        if not isinstance(customer_id, str):
            raise TypeError("customer_id must be a string.")

        customer_id = customer_id.strip()
        if not customer_id:
            raise ValueError("customer_id cannot be empty.")

        data = self._storage_service.load_data()
        customers = data["customers"]
        for customer_data in customers:
            if customer_data.get("id") == customer_id:
                return Customer.from_dict(customer_data)

        return None

    def get_all_customers(self) -> list[Customer]:
        """Retrieve all customers in the system.

        Returns:
            All customers currently stored in the system.
        """
        data = self._storage_service.load_data()
        return [
            Customer.from_dict(customer_data)
            for customer_data in data["customers"]
        ]

    def update_customer(self, customer: Customer) -> None:
        """Update an existing customer in the system.

        Args:
            customer: Customer containing the updated data.

        Raises:
            TypeError: If customer is not a Customer instance.
            ValueError: If no customer exists with the same identifier.
        """
        if not isinstance(customer, Customer):
            raise TypeError("customer must be an instance of Customer.")

        data = self._storage_service.load_data()
        customers = data["customers"]

        for index, existing_customer in enumerate(customers):
            if existing_customer.get("id") == customer.id:
                customer.update_timestamp()
                customers[index] = customer.to_dict()
                self._storage_service.save_data(data)
                return

        raise ValueError(f"Customer with ID '{customer.id}' does not exist.")

    def delete_customer(self, customer_id: str) -> None:
        """Remove a customer from the system.

        Args:
            customer_id: Unique identifier of the customer to remove.

        Raises:
            TypeError: If customer_id is not a string.
            ValueError: If customer_id is empty after stripping whitespace or no
                customer exists with the specified identifier.
        """
        if not isinstance(customer_id, str):
            raise TypeError("customer_id must be a string.")

        customer_id = customer_id.strip()
        if not customer_id:
            raise ValueError("customer_id cannot be empty.")

        data = self._storage_service.load_data()
        customers = data["customers"]

        for index, customer_data in enumerate(customers):
            if customer_data.get("id") == customer_id:
                del customers[index]
                self._storage_service.save_data(data)
                return

        raise ValueError(f"Customer with ID '{customer_id}' does not exist.")

    def search_customers(self, keyword: str) -> list[Customer]:
        """Find customers that match a keyword.

        Args:
            keyword: Text used to search the customer system.

        Returns:
            Customers that match the provided keyword.

        Raises:
            TypeError: If keyword is not a string.
            ValueError: If keyword is empty after stripping whitespace.
        """
        if not isinstance(keyword, str):
            raise TypeError("keyword must be a string.")

        keyword = keyword.strip()
        if not keyword:
            raise ValueError("keyword cannot be empty.")

        normalized_keyword = keyword.casefold()
        data = self._storage_service.load_data()
        customers = data["customers"]
        matching_customers: list[Customer] = []

        for customer_data in customers:
            searchable_values = (
                customer_data.get("id", ""),
                customer_data.get("first_name", ""),
                customer_data.get("last_name", ""),
                customer_data.get("email", ""),
                customer_data.get("phone", ""),
                customer_data.get("address", ""),
            )
            if any(
                normalized_keyword in str(value).casefold()
                for value in searchable_values
            ):
                matching_customers.append(Customer.from_dict(customer_data))

        return matching_customers
