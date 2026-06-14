from abc import ABC, abstractmethod


class DatabaseAdapter(ABC):

    @abstractmethod
    def execute(self, sql: str) -> list[dict]:
        """Execute a SQL query and return rows as list of dicts."""
        pass

    @abstractmethod
    def get_schema(self) -> dict:
        """Return table -> [columns] mapping for this database."""
        pass

    @abstractmethod
    def test_connection(self) -> bool:
        """Return True if the database is reachable."""
        pass
