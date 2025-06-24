from __future__ import annotations

from abc import ABC, abstractmethod

from openhands.storage.data_models.user import (
    CreditTransaction,
    User,
    UserProfile,
    UserRegistration,
)


class UserStore(ABC):
    """Abstract base class for user storage"""

    @abstractmethod
    async def create_user(
        self, user_data: UserRegistration, password_hash: str
    ) -> User:
        """Create a new user"""

    @abstractmethod
    async def get_user_by_id(self, user_id: str) -> User | None:
        """Get user by ID"""

    @abstractmethod
    async def get_user_by_email(self, email: str) -> User | None:
        """Get user by email"""

    @abstractmethod
    async def update_user(self, user_id: str, user_data: UserProfile) -> User | None:
        """Update user profile"""

    @abstractmethod
    async def update_user_credits(self, user_id: str, credits: float) -> bool:
        """Update user credits"""

    @abstractmethod
    async def deduct_credits(
        self,
        user_id: str,
        amount: float,
        description: str,
        metadata: dict | None = None,
    ) -> bool:
        """Deduct credits from user account and record transaction"""

    @abstractmethod
    async def add_credits(
        self,
        user_id: str,
        amount: float,
        description: str,
        metadata: dict | None = None,
    ) -> bool:
        """Add credits to user account and record transaction"""

    @abstractmethod
    async def get_credit_transactions(
        self, user_id: str, limit: int = 100
    ) -> list[CreditTransaction]:
        """Get user's credit transaction history"""

    @abstractmethod
    async def update_last_login(self, user_id: str) -> bool:
        """Update user's last login timestamp"""

    @abstractmethod
    async def verify_user_email(self, user_id: str) -> bool:
        """Mark user email as verified"""

    @abstractmethod
    async def deactivate_user(self, user_id: str) -> bool:
        """Deactivate user account"""

    @abstractmethod
    async def get_user_workspace_path(self, user_id: str) -> str | None:
        """Get user's workspace path"""

    @abstractmethod
    async def set_user_workspace_path(self, user_id: str, workspace_path: str) -> bool:
        """Set user's workspace path"""
