from __future__ import annotations

import os

from openhands.storage.local import LocalFileStore
from openhands.storage.settings.file_settings_store import FileSettingsStore


class UserFileSettingsStore(FileSettingsStore):
    """User-specific file settings store for multi-tenant SaaS"""

    def __init__(self, user_id: str | None = None):
        self.user_id = user_id

        if user_id:
            # Create user-specific settings directory
            user_settings_dir = f'/workspaces/user_{user_id}/.openhands'
            os.makedirs(user_settings_dir, exist_ok=True)
            settings_file = os.path.join(user_settings_dir, 'settings.json')
        else:
            # Fallback to default location for non-authenticated users
            settings_file = os.path.join(os.getcwd(), 'settings.json')

        file_store = LocalFileStore(os.path.dirname(settings_file))
        super().__init__(file_store)

    @classmethod
    async def get_instance(
        cls, config, user_id: str | None = None
    ) -> UserFileSettingsStore:
        """Get instance of UserFileSettingsStore"""
        return cls(user_id=user_id)
