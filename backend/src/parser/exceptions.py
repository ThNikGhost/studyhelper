"""Custom exceptions for parser module."""


class ParserException(Exception):
    """Base exception for parser errors."""

    pass


class PageLoadError(ParserException):
    """Raised when page fails to load or times out."""

    pass


class ElementNotFoundError(ParserException):
    """Raised when expected element is not found on page."""

    pass


class DataExtractionError(ParserException):
    """Raised when data extraction fails."""

    pass


class MappingError(ParserException):
    """Raised when mapping raw data to schema fails."""

    pass
