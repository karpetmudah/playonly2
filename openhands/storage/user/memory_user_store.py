"""In-memory user store implementation for testing purposes"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Dict, List

from openhands.storage.data_models.user import (
    CreditTransaction,
    User,
    UserProfile,
    UserRegistration,
)
from openhands.storage.user.user_store import UserStore


class MemoryUserStore(UserStore):
    """In-memory implementation of UserStore for testing"""

    def __init__(self):
        self._users: Dict[str, User] = {}
        self._users_by_email: Dict[str, str] = {}  # email -> user_id mapping
        self._credit_transactions: Dict[str, List[CreditTransaction]] = {}

    async def create_user(
        self, user_data: UserRegistration, password_hash: str
    ) -> User:
        """Create a new user"""
        user_id = str(uuid.uuid4())
        now = datetime.utcnow()
        
        user = User(
            user_id=user_id,
            email=user_data.email,
            full_name=user_data.full_name,
            password_hash=password_hash,
            credits=0.0,
            is_active=True,
            is_verified=False,
            created_at=now,
            updated_at=now,
            last_login=None,
            workspace_path=None,
        )
        
        self._users[user_id] = user
        self._users_by_email[user_data.email] = user_id
        self._credit_transactions[user_id] = []
        
        return user

    async def get_user_by_id(self, user_id: str) -> User | None:
        """Get user by ID"""
        return self._users.get(user_id)

    async def get_user_by_email(self, email: str) -> User | None:
        """Get user by email"""
        user_id = self._users_by_email.get(email)
        if user_id:
            return self._users.get(user_id)
        return None

    async def update_user(self, user_id: str, user_data: UserProfile) -> User | None:
        """Update user profile"""
        user = self._users.get(user_id)
        if not user:
            return None
            
        user.full_name = user_data.full_name
        user.updated_at = datetime.utcnow()
        
        return user

    async def update_user_credits(self, user_id: str, credits: float) -> bool:
        """Update user credits"""
        user = self._users.get(user_id)
        if not user:
            return False
            
        user.credits = credits
        user.updated_at = datetime.utcnow()
        return True

    async def deduct_credits(
        self,
        user_id: str,
        amount: float,
        description: str,
        metadata: dict | None = None,
    ) -> bool:
        """Deduct credits from user account and record transaction"""
        user = self._users.get(user_id)
        if not user or user.credits < amount:
            return False
            
        user.credits -= amount
        user.updated_at = datetime.utcnow()
        
        transaction = CreditTransaction(
            transaction_id=str(uuid.uuid4()),
            user_id=user_id,
            amount=-amount,
            transaction_type="usage",
            description=description,
            metadata=metadata or {},
            created_at=datetime.utcnow(),
        )
        
        if user_id not in self._credit_transactions:
            self._credit_transactions[user_id] = []
        self._credit_transactions[user_id].append(transaction)
        
        return True

    async def add_credits(
        self,
        user_id: str,
        amount: float,
        description: str,
        metadata: dict | None = None,
    ) -> bool:
        """Add credits to user account and record transaction"""
        user = self._users.get(user_id)
        if not user:
            return False
            
        user.credits += amount
        user.updated_at = datetime.utcnow()
        
        transaction = CreditTransaction(
            transaction_id=str(uuid.uuid4()),
            user_id=user_id,
            amount=amount,
            transaction_type="purchase",
            description=description,
            metadata=metadata or {},
            created_at=datetime.utcnow(),
        )
        
        if user_id not in self._credit_transactions:
            self._credit_transactions[user_id] = []
        self._credit_transactions[user_id].append(transaction)
        
        return True

    async def get_credit_transactions(
        self, user_id: str, limit: int = 100
    ) -> list[CreditTransaction]:
        """Get user's credit transaction history"""
        transactions = self._credit_transactions.get(user_id, [])
        return sorted(transactions, key=lambda t: t.created_at, reverse=True)[:limit]

    async def update_last_login(self, user_id: str) -> bool:
        """Update user's last login timestamp"""
        user = self._users.get(user_id)
        if not user:
            return False
            
        user.last_login = datetime.utcnow()
        user.updated_at = datetime.utcnow()
        return True

    async def verify_user_email(self, user_id: str) -> bool:
        """Mark user email as verified"""
        user = self._users.get(user_id)
        if not user:
            return False
            
        user.is_verified = True
        user.updated_at = datetime.utcnow()
        return True

    async def deactivate_user(self, user_id: str) -> bool:
        """Deactivate user account"""
        user = self._users.get(user_id)
        if not user:
            return False
            
        user.is_active = False
        user.updated_at = datetime.utcnow()
        return True

    async def get_user_workspace_path(self, user_id: str) -> str | None:
        """Get user's workspace path"""
        user = self._users.get(user_id)
        return user.workspace_path if user else None

    async def set_user_workspace_path(self, user_id: str, workspace_path: str) -> bool:
        """Set user's workspace path"""
        user = self._users.get(user_id)
        if not user:
            return False
            
        user.workspace_path = workspace_path
        user.updated_at = datetime.utcnow()
        return True