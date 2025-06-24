from __future__ import annotations

import os
from dataclasses import dataclass
from datetime import datetime, timedelta

import jwt
from fastapi import HTTPException, Request, status
from pydantic import SecretStr

from openhands.integrations.provider import PROVIDER_TOKEN_TYPE
from openhands.server import shared
from openhands.server.settings import Settings
from openhands.server.user_auth.user_auth import AuthType, UserAuth
from openhands.storage.data_models.user_secrets import UserSecrets
from openhands.storage.secrets.secrets_store import SecretsStore
from openhands.storage.settings.settings_store import SettingsStore
from openhands.storage.user.user_store import UserStore
from openhands.utils.import_utils import get_impl


@dataclass
class SaaSUserAuth(UserAuth):
    """SaaS user authentication mechanism with JWT tokens"""

    _settings: Settings | None = None
    _settings_store: SettingsStore | None = None
    _secrets_store: SecretsStore | None = None
    _user_secrets: UserSecrets | None = None
    _user_id: str | None = None
    _user_email: str | None = None
    _access_token: SecretStr | None = None
    _user_store: UserStore | None = None

    def __init__(
        self,
        user_id: str | None = None,
        user_email: str | None = None,
        access_token: str | None = None,
    ):
        self._user_id = user_id
        self._user_email = user_email
        self._access_token = SecretStr(access_token) if access_token else None

    async def get_user_id(self) -> str | None:
        """Get the unique identifier for the current user"""
        return self._user_id

    async def get_user_email(self) -> str | None:
        """Get the email for the current user"""
        return self._user_email

    async def get_access_token(self) -> SecretStr | None:
        """Get the access token for the current user"""
        return self._access_token

    async def get_user_settings_store(self) -> SettingsStore:
        """Get the settings store for the current user"""
        settings_store = self._settings_store
        if settings_store:
            return settings_store

        user_id = await self.get_user_id()
        settings_store = await shared.SettingsStoreImpl.get_instance(
            shared.config, user_id
        )
        if settings_store is None:
            raise ValueError('Failed to get settings store instance')
        self._settings_store = settings_store
        return settings_store

    async def get_user_settings(self) -> Settings | None:
        """Get the user settings for the current user"""
        settings = self._settings
        if settings:
            return settings

        settings_store = await self.get_user_settings_store()
        settings = await settings_store.load()

        # Set user email in settings if not already set
        if settings and not settings.email:
            user_email = await self.get_user_email()
            if user_email:
                settings.email = user_email
                await settings_store.store(settings)

        self._settings = settings
        return settings

    async def get_secrets_store(self) -> SecretsStore:
        """Get secrets store for the current user"""
        secrets_store = self._secrets_store
        if secrets_store:
            return secrets_store

        user_id = await self.get_user_id()
        secret_store = await shared.SecretsStoreImpl.get_instance(
            shared.config, user_id
        )
        if secret_store is None:
            raise ValueError('Failed to get secrets store instance')
        self._secrets_store = secret_store
        return secret_store

    async def get_user_secrets(self) -> UserSecrets | None:
        """Get the user's secrets"""
        user_secrets = self._user_secrets
        if user_secrets:
            return user_secrets

        secrets_store = await self.get_secrets_store()
        user_secrets = await secrets_store.load()
        self._user_secrets = user_secrets
        return user_secrets

    async def get_provider_tokens(self) -> PROVIDER_TOKEN_TYPE | None:
        """Get the provider tokens for the current user"""
        user_secrets = await self.get_user_secrets()
        if user_secrets is None:
            return None
        return user_secrets.provider_tokens

    def get_auth_type(self) -> AuthType | None:
        """Get the authentication type"""
        return AuthType.BEARER

    async def get_user_store(self) -> UserStore:
        """Get the user store instance"""
        if self._user_store is None:
            user_store_class = os.getenv(
                'USER_STORE_CLASS',
                'openhands.storage.user.mongodb_user_store.MongoDBUserStore',
            )
            user_store_impl = get_impl(UserStore, user_store_class)
            self._user_store = user_store_impl()
        return self._user_store

    @classmethod
    async def get_instance(cls, request: Request) -> UserAuth:
        """Get an instance of SaaSUserAuth from the request"""
        # Try to get JWT token from Authorization header
        authorization = request.headers.get('Authorization')
        if not authorization or not authorization.startswith('Bearer '):
            # No token provided - return instance with no user
            return cls()

        token = authorization.split(' ')[1]

        try:
            # Decode JWT token
            secret_key = os.getenv('JWT_SECRET_KEY', 'your-secret-key-change-this')
            payload = jwt.decode(token, secret_key, algorithms=['HS256'])

            user_id = payload.get('user_id')
            user_email = payload.get('email')

            if not user_id:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail='Invalid token: missing user_id',
                )

            # Verify token expiration
            exp = payload.get('exp')
            if exp and datetime.utcfromtimestamp(exp) < datetime.utcnow():
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED, detail='Token has expired'
                )

            return cls(user_id=user_id, user_email=user_email, access_token=token)

        except jwt.InvalidTokenError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid token'
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f'Authentication failed: {str(e)}',
            )


def create_access_token(
    user_id: str, email: str, expires_delta: timedelta | None = None
) -> str:
    """Create a JWT access token"""
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=7)  # Default 7 days

    to_encode = {
        'user_id': user_id,
        'email': email,
        'exp': expire,
        'iat': datetime.utcnow(),
    }

    secret_key = os.getenv('JWT_SECRET_KEY', 'your-secret-key-change-this')
    encoded_jwt = jwt.encode(to_encode, secret_key, algorithm='HS256')
    return encoded_jwt


def verify_token(token: str) -> dict:
    """Verify and decode a JWT token"""
    secret_key = os.getenv('JWT_SECRET_KEY', 'your-secret-key-change-this')
    try:
        payload = jwt.decode(token, secret_key, algorithms=['HS256'])
        return payload
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid token'
        )
