"""
API v1 Dependencies.
Re-exports common dependencies from core for convenience.
"""
from app.core.dependencies import (
    get_current_user,
    get_current_active_user,
    RoleChecker,
    ManagerTypeChecker,
    bearer_scheme,
)

__all__ = [
    "get_current_user",
    "get_current_active_user",
    "RoleChecker",
    "ManagerTypeChecker",
    "bearer_scheme",
]
