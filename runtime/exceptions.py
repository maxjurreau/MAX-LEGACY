"""Exception types for MAX-LEGACY runtime and API layers."""
from __future__ import annotations


class MAXLegacyError(Exception):
    """Base exception for MAX-LEGACY runtime errors."""


class ValidationError(MAXLegacyError):
    """Raised when a knowledge object or event fails validation."""


class StoreError(MAXLegacyError):
    """Raised when persistence operations fail."""


class RuntimeConfigError(MAXLegacyError):
    """Raised when runtime configuration is invalid."""


class DomainNotFoundError(MAXLegacyError):
    """Raised when a requested domain is unknown."""


class PromotionError(MAXLegacyError):
    """Raised when promotion validation or propagation fails."""
