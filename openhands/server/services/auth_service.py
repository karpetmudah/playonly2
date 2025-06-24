from __future__ import annotations

import os

import bcrypt
import jwt
from fastapi import HTTPException, status

from openhands.core.logger import openhands_logger as logger
from openhands.server.user_auth.saas_user_auth import create_access_token
from openhands.storage.data_models.user import (
    TokenResponse,
    UserLogin,
    UserProfile,
    UserRegistration,
    UserResponse,
)
from openhands.storage.user.user_store import UserStore
from openhands.utils.import_utils import get_impl


class AuthService:
    """Authentication service for user management"""

    def __init__(self):
        self.user_store: UserStore | None = None
        self.jwt_secret = os.getenv('JWT_SECRET', 'your-secret-key')
        self.jwt_algorithm = 'HS256'

    async def get_user_store(self) -> UserStore:
        """Get the user store instance"""
        if self.user_store is None:
            user_store_class = os.getenv(
                'USER_STORE_CLASS',
                'openhands.storage.user.mongodb_user_store.MongoDBUserStore',
            )
            user_store_impl = get_impl(UserStore, user_store_class)
            self.user_store = user_store_impl()
        return self.user_store

    def hash_password(self, password: str) -> str:
        """Hash a password using bcrypt"""
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')

    def verify_password(self, password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))

    async def register_user(self, user_data: UserRegistration) -> TokenResponse:
        """Register a new user"""
        user_store = await self.get_user_store()

        # Check if user already exists
        existing_user = await user_store.get_user_by_email(user_data.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='User with this email already exists',
            )

        # Hash password
        password_hash = self.hash_password(user_data.password)

        # Create user
        try:
            user = await user_store.create_user(user_data, password_hash)

            # Create workspace directory
            if user.workspace_path:
                await self._create_user_workspace(user.user_id, user.workspace_path)

            # Create access token
            access_token = create_access_token(user.user_id, user.email)

            # Update last login
            await user_store.update_last_login(user.user_id)

            logger.info(f'User registered successfully: {user.email}')

            return TokenResponse(
                access_token=access_token,
                expires_in=7 * 24 * 60 * 60,  # 7 days in seconds
                user=UserResponse(
                    user_id=user.user_id,
                    email=user.email,
                    full_name=user.full_name,
                    is_active=user.is_active,
                    is_verified=user.is_verified,
                    credits=user.credits,
                    total_credits_purchased=user.total_credits_purchased,
                    total_credits_used=user.total_credits_used,
                    created_at=user.created_at,
                    last_login=user.last_login,
                ),
            )
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    async def login_user(self, login_data: UserLogin) -> TokenResponse:
        """Login a user"""
        user_store = await self.get_user_store()

        # Get user by email
        user = await user_store.get_user_by_email(login_data.email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='Invalid email or password',
            )

        # Check if user is active
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='Account is deactivated',
            )

        # Verify password
        if not self.verify_password(login_data.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='Invalid email or password',
            )

        # Create access token
        access_token = create_access_token(user.user_id, user.email)

        # Update last login
        await user_store.update_last_login(user.user_id)

        logger.info(f'User logged in successfully: {user.email}')

        return TokenResponse(
            access_token=access_token,
            expires_in=7 * 24 * 60 * 60,  # 7 days in seconds
            user=UserResponse(
                user_id=user.user_id,
                email=user.email,
                full_name=user.full_name,
                is_active=user.is_active,
                is_verified=user.is_verified,
                credits=user.credits,
                total_credits_purchased=user.total_credits_purchased,
                total_credits_used=user.total_credits_used,
                created_at=user.created_at,
                last_login=user.last_login,
            ),
        )

    async def get_user_profile(self, user_id: str) -> UserResponse:
        """Get user profile"""
        user_store = await self.get_user_store()

        user = await user_store.get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail='User not found'
            )

        return UserResponse(
            user_id=user.user_id,
            email=user.email,
            full_name=user.full_name,
            is_active=user.is_active,
            is_verified=user.is_verified,
            credits=user.credits,
            total_credits_purchased=user.total_credits_purchased,
            total_credits_used=user.total_credits_used,
            created_at=user.created_at,
            last_login=user.last_login,
        )

    async def update_user_profile(
        self, user_id: str, profile_data: UserProfile
    ) -> UserResponse:
        """Update user profile"""
        user_store = await self.get_user_store()

        # Check if email is being changed and if it's already taken
        if profile_data.email:
            existing_user = await user_store.get_user_by_email(profile_data.email)
            if existing_user and existing_user.user_id != user_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail='Email is already taken by another user',
                )

        updated_user = await user_store.update_user(user_id, profile_data)
        if not updated_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail='User not found'
            )

        logger.info(f'User profile updated: {updated_user.email}')

        return UserResponse(
            user_id=updated_user.user_id,
            email=updated_user.email,
            full_name=updated_user.full_name,
            is_active=updated_user.is_active,
            is_verified=updated_user.is_verified,
            credits=updated_user.credits,
            total_credits_purchased=updated_user.total_credits_purchased,
            total_credits_used=updated_user.total_credits_used,
            created_at=updated_user.created_at,
            last_login=updated_user.last_login,
        )

    async def add_credits(
        self, user_id: str, amount: float, description: str = 'Credit purchase'
    ) -> bool:
        """Add credits to user account"""
        user_store = await self.get_user_store()

        success = await user_store.add_credits(
            user_id=user_id,
            amount=amount,
            description=description,
            metadata={'source': 'manual_addition'},
        )

        if success:
            logger.info(f'Added {amount} credits to user {user_id}')

        return success

    async def deduct_credits(
        self,
        user_id: str,
        amount: float,
        description: str,
        metadata: dict | None = None,
    ) -> bool:
        """Deduct credits from user account"""
        user_store = await self.get_user_store()

        success = await user_store.deduct_credits(
            user_id=user_id, amount=amount, description=description, metadata=metadata
        )

        if success:
            logger.info(f'Deducted {amount} credits from user {user_id}')

        return success

    async def get_user_credits(self, user_id: str) -> float:
        """Get user's current credit balance"""
        user_store = await self.get_user_store()

        user = await user_store.get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail='User not found'
            )

        return user.credits

    async def verify_token(self, token: str) -> str:
        """
        Verify JWT token and return user ID

        Args:
            token: JWT token

        Returns:
            str: User ID

        Raises:
            Exception: If token is invalid
        """
        try:
            payload = jwt.decode(
                token, self.jwt_secret, algorithms=[self.jwt_algorithm]
            )
            user_id = payload.get('sub')
            if not user_id:
                raise Exception('Invalid token: no user ID')
            return user_id
        except jwt.ExpiredSignatureError:
            raise Exception('Token has expired')
        except jwt.InvalidTokenError:
            raise Exception('Invalid token')

    async def _create_user_workspace(self, user_id: str, workspace_path: str):
        """Create user's workspace directory"""
        try:
            os.makedirs(workspace_path, exist_ok=True)
            logger.info(
                f'Created workspace directory for user {user_id}: {workspace_path}'
            )
        except Exception as e:
            logger.error(
                f'Failed to create workspace directory for user {user_id}: {e}'
            )
            # Don't raise exception as this is not critical for user registration
