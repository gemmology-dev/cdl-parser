"""
CDL Parser Exceptions.

Custom exception classes for Crystal Description Language parsing errors.
"""


class CDLError(Exception):
    """Base exception for CDL-related errors."""

    pass


class ParseError(CDLError):
    """Raised when CDL parsing fails.

    Attributes:
        message: Human-readable error description
        position: Character position in the input string where error occurred
        line: Optional line number (for multi-line inputs)
        column: Optional column number
    """

    def __init__(self, message: str, position: int = -1, line: int = -1, column: int = -1):
        self.message = message
        self.position = position
        self.line = line
        self.column = column
        super().__init__(self._format_message())

    def _format_message(self) -> str:
        parts = [self.message]
        if self.position >= 0:
            parts.append(f"at position {self.position}")
        if self.line >= 0:
            parts.append(f"(line {self.line}")
            if self.column >= 0:
                parts.append(f", column {self.column})")
            else:
                parts.append(")")
        return " ".join(parts)


class ValidationError(CDLError):
    """Raised when CDL validation fails.

    This is raised when the CDL syntax is correct but the content
    is semantically invalid (e.g., invalid point group for system).

    Attributes:
        message: Human-readable error description
        field: The field or component that failed validation
        value: The invalid value
    """

    def __init__(self, message: str, field: str = "", value: str = ""):
        self.message = message
        self.field = field
        self.value = value
        super().__init__(self._format_message())

    def _format_message(self) -> str:
        if self.field and self.value:
            return f"{self.message}: {self.field}='{self.value}'"
        elif self.field:
            return f"{self.message}: {self.field}"
        return self.message
