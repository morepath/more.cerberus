from typing import Any


class ValidationError(Exception):
    def __init__(self, errors: dict[str, Any]) -> None:
        super().__init__("Cerberus validation error")
        self.errors: dict[str, Any] = errors
