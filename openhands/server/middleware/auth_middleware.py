from __future__ import annotations

import os

from fastapi import HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from openhands.server.services.auth_service import AuthService


class AuthMiddleware:
    """Authentication middleware for SaaS mode"""

    def __init__(self):
        self.auth_service = AuthService()
        self.security = HTTPBearer(auto_error=False)
        self.is_saas_mode = os.getenv('OPENHANDS_CONFIG_CLS', '').endswith(
            'SaaSServerConfig'
        )

    async def get_current_user(
        self, request: Request, credentials: HTTPAuthorizationCredentials | None = None
    ) -> str | None:
        """
        Extract user ID from JWT token if in SaaS mode

        Returns:
            str: User ID if authenticated in SaaS mode
            None: If not in SaaS mode or not authenticated
        """
        if not self.is_saas_mode:
            return None

        if not credentials:
            return None

        try:
            user_id = await self.auth_service.verify_token(credentials.credentials)
            return user_id
        except Exception:
            return None

    async def require_auth(
        self, request: Request, credentials: HTTPAuthorizationCredentials | None = None
    ) -> str:
        """
        Require authentication in SaaS mode

        Returns:
            str: User ID

        Raises:
            HTTPException: If not authenticated in SaaS mode
        """
        if not self.is_saas_mode:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Authentication not required in non-SaaS mode',
            )

        if not credentials:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='Authentication required',
                headers={'WWW-Authenticate': 'Bearer'},
            )

        try:
            user_id = await self.auth_service.verify_token(credentials.credentials)
            return user_id
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f'Invalid authentication credentials: {str(e)}',
                headers={'WWW-Authenticate': 'Bearer'},
            )

    def get_user_workspace_path(self, user_id: str) -> str:
        """Get the workspace path for a specific user"""
        return f'/workspaces/user_{user_id}'

    def ensure_user_workspace(self, user_id: str) -> str:
        """Ensure user workspace directory exists and return path"""
        workspace_path = self.get_user_workspace_path(user_id)
        os.makedirs(workspace_path, exist_ok=True)
        return workspace_path


# Global instance
auth_middleware = AuthMiddleware()
