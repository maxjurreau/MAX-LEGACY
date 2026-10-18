# Compatibility shim: allow code or deployment configs that expect cloudflare.r2.storage_adapter
# to import the implementation from the top-level r2 package.
from r2.storage_adapter import R2StorageAdapter

__all__ = ["R2StorageAdapter"]
