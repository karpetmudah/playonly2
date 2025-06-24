from __future__ import annotations

import os
import uuid
from datetime import datetime
from typing import Any

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo.errors import DuplicateKeyError

from openhands.core.logger import openhands_logger as logger
from openhands.storage.data_models.user import (
    CreditTransaction,
    User,
    UserProfile,
    UserRegistration,
)
from openhands.storage.user.user_store import UserStore


class MongoDBUserStore(UserStore):
    """MongoDB implementation of UserStore"""

    def __init__(
        self, mongodb_url: str | None = None, database_name: str = 'openhands_saas'
    ):
        self.mongodb_url = mongodb_url or os.getenv(
            'MONGODB_URL', 'mongodb://localhost:27017'
        )
        self.database_name = database_name
        self.client: AsyncIOMotorClient | None = None
        self.db: AsyncIOMotorDatabase | None = None

    async def _get_database(self) -> AsyncIOMotorDatabase:
        """Get database connection"""
        if self.db is None:
            self.client = AsyncIOMotorClient(self.mongodb_url)
            self.db = self.client[self.database_name]

            # Create indexes
            await self._create_indexes()

        return self.db

    async def _create_indexes(self):
        """Create necessary database indexes"""
        db = await self._get_database()

        # Users collection indexes
        await db.users.create_index('email', unique=True)
        await db.users.create_index('user_id', unique=True)

        # Credit transactions collection indexes
        await db.credit_transactions.create_index('user_id')
        await db.credit_transactions.create_index('created_at')
        await db.credit_transactions.create_index([('user_id', 1), ('created_at', -1)])

    async def create_user(
        self, user_data: UserRegistration, password_hash: str
    ) -> User:
        """Create a new user"""
        db = await self._get_database()

        user_id = str(uuid.uuid4())
        workspace_path = f'/workspaces/user_{user_id}'

        user = User(
            user_id=user_id,
            email=user_data.email,
            password_hash=password_hash,
            full_name=user_data.full_name,
            workspace_path=workspace_path,
        )

        try:
            await db.users.insert_one(user.model_dump())
            logger.info(f'Created new user: {user.email}')
            return user
        except DuplicateKeyError:
            raise ValueError('User with this email already exists')

    async def get_user_by_id(self, user_id: str) -> User | None:
        """Get user by ID"""
        db = await self._get_database()

        user_doc = await db.users.find_one({'user_id': user_id})
        if user_doc:
            return User(**user_doc)
        return None

    async def get_user_by_email(self, email: str) -> User | None:
        """Get user by email"""
        db = await self._get_database()

        user_doc = await db.users.find_one({'email': email})
        if user_doc:
            return User(**user_doc)
        return None

    async def update_user(self, user_id: str, user_data: UserProfile) -> User | None:
        """Update user profile"""
        db = await self._get_database()

        update_data: dict[str, Any] = {'updated_at': datetime.utcnow()}

        if user_data.full_name is not None:
            update_data['full_name'] = user_data.full_name

        if user_data.email is not None:
            update_data['email'] = user_data.email
            update_data['is_verified'] = False  # Re-verify email if changed

        result = await db.users.update_one({'user_id': user_id}, {'$set': update_data})

        if result.modified_count > 0:
            return await self.get_user_by_id(user_id)
        return None

    async def update_user_credits(self, user_id: str, credits: float) -> bool:
        """Update user credits"""
        db = await self._get_database()

        result = await db.users.update_one(
            {'user_id': user_id},
            {'$set': {'credits': credits, 'updated_at': datetime.utcnow()}},
        )

        return result.modified_count > 0

    async def deduct_credits(
        self,
        user_id: str,
        amount: float,
        description: str,
        metadata: dict | None = None,
    ) -> bool:
        """Deduct credits from user account and record transaction"""
        db = await self._get_database()

        # Start a transaction to ensure atomicity
        if not self.client:
            raise RuntimeError('MongoDB client not initialized')
        async with await self.client.start_session() as session:
            async with session.start_transaction():
                # Check if user has enough credits
                user = await self.get_user_by_id(user_id)
                if not user or user.credits < amount:
                    return False

                # Deduct credits
                new_credits = user.credits - amount
                new_total_used = user.total_credits_used + amount

                await db.users.update_one(
                    {'user_id': user_id},
                    {
                        '$set': {
                            'credits': new_credits,
                            'total_credits_used': new_total_used,
                            'updated_at': datetime.utcnow(),
                        }
                    },
                    session=session,
                )

                # Record transaction
                transaction = CreditTransaction(
                    transaction_id=str(uuid.uuid4()),
                    user_id=user_id,
                    amount=-amount,  # Negative for deduction
                    transaction_type='usage',
                    description=description,
                    metadata=metadata,
                )

                await db.credit_transactions.insert_one(
                    transaction.model_dump(), session=session
                )

                logger.info(
                    f'Deducted {amount} credits from user {user_id}. New balance: {new_credits}'
                )
                return True

    async def add_credits(
        self,
        user_id: str,
        amount: float,
        description: str,
        metadata: dict | None = None,
    ) -> bool:
        """Add credits to user account and record transaction"""
        db = await self._get_database()

        # Start a transaction to ensure atomicity
        if not self.client:
            raise RuntimeError('MongoDB client not initialized')
        async with await self.client.start_session() as session:
            async with session.start_transaction():
                user = await self.get_user_by_id(user_id)
                if not user:
                    return False

                # Add credits
                new_credits = user.credits + amount
                new_total_purchased = user.total_credits_purchased + amount

                await db.users.update_one(
                    {'user_id': user_id},
                    {
                        '$set': {
                            'credits': new_credits,
                            'total_credits_purchased': new_total_purchased,
                            'updated_at': datetime.utcnow(),
                        }
                    },
                    session=session,
                )

                # Record transaction
                transaction = CreditTransaction(
                    transaction_id=str(uuid.uuid4()),
                    user_id=user_id,
                    amount=amount,  # Positive for addition
                    transaction_type='purchase',
                    description=description,
                    metadata=metadata,
                )

                await db.credit_transactions.insert_one(
                    transaction.model_dump(), session=session
                )

                logger.info(
                    f'Added {amount} credits to user {user_id}. New balance: {new_credits}'
                )
                return True

    async def get_credit_transactions(
        self, user_id: str, limit: int = 100
    ) -> list[CreditTransaction]:
        """Get user's credit transaction history"""
        db = await self._get_database()

        cursor = (
            db.credit_transactions.find({'user_id': user_id})
            .sort('created_at', -1)
            .limit(limit)
        )

        transactions = []
        async for doc in cursor:
            transactions.append(CreditTransaction(**doc))

        return transactions

    async def update_last_login(self, user_id: str) -> bool:
        """Update user's last login timestamp"""
        db = await self._get_database()

        result = await db.users.update_one(
            {'user_id': user_id}, {'$set': {'last_login': datetime.utcnow()}}
        )

        return result.modified_count > 0

    async def verify_user_email(self, user_id: str) -> bool:
        """Mark user email as verified"""
        db = await self._get_database()

        result = await db.users.update_one(
            {'user_id': user_id},
            {'$set': {'is_verified': True, 'updated_at': datetime.utcnow()}},
        )

        return result.modified_count > 0

    async def deactivate_user(self, user_id: str) -> bool:
        """Deactivate user account"""
        db = await self._get_database()

        result = await db.users.update_one(
            {'user_id': user_id},
            {'$set': {'is_active': False, 'updated_at': datetime.utcnow()}},
        )

        return result.modified_count > 0

    async def get_user_workspace_path(self, user_id: str) -> str | None:
        """Get user's workspace path"""
        user = await self.get_user_by_id(user_id)
        return user.workspace_path if user else None

    async def set_user_workspace_path(self, user_id: str, workspace_path: str) -> bool:
        """Set user's workspace path"""
        db = await self._get_database()

        result = await db.users.update_one(
            {'user_id': user_id},
            {
                '$set': {
                    'workspace_path': workspace_path,
                    'updated_at': datetime.utcnow(),
                }
            },
        )

        return result.modified_count > 0

    async def close(self):
        """Close database connection"""
        if self.client:
            self.client.close()
