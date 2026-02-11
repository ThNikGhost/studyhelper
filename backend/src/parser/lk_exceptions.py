"""Custom exceptions for LK parser module."""


class LkParserException(Exception):
    """Base exception for LK parser errors."""


class LkAuthError(LkParserException):
    """Raised when authentication to LK fails."""


class LkSessionExpired(LkParserException):
    """Raised when LK session has expired."""


class LkDataError(LkParserException):
    """Raised when LK returns unexpected data format."""
