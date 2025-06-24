from __future__ import annotations

import os

from openhands.storage.local import LocalFileStore
from openhands.storage.secrets.file_secrets_store import FileSecretsStore


class UserFileSecretsStore(FileSecretsStore):
    """User-specific file secrets store for multi-tenant SaaS"""

    def __init__(self, user_id: str | None = None):
        self.user_id = user_id

        if user_id:
            # Create user-specific secrets directory
            user_secrets_dir = f'/workspaces/user_{user_id}/.openhands'
            os.makedirs(user_secrets_dir, exist_ok=True)
            secrets_file = os.path.join(user_secrets_dir, 'secrets.json')
        else:
            # Fallback to default location for non-authenticated users
            secrets_file = os.path.join(os.getcwd(), 'secrets.json')

        file_store = LocalFileStore(os.path.dirname(secrets_file))
        super().__init__(file_store)

    @classmethod
    async def get_instance(
        cls, config, user_id: str | None = None
    ) -> UserFileSecretsStore:
        """Get instance of UserFileSecretsStore"""
        return cls(user_id=user_id)
