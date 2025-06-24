from __future__ import annotations

import os

from openhands.storage.conversation.file_conversation_store import FileConversationStore
from openhands.storage.local import LocalFileStore


class UserFileConversationStore(FileConversationStore):
    """User-specific file conversation store for multi-tenant SaaS"""

    def __init__(self, user_id: str | None = None):
        self.user_id = user_id

        if user_id:
            # Create user-specific conversations directory in writable location
            user_conversations_dir = (
                f'/tmp/openhands/user_{user_id}/.openhands/conversations'
            )
            os.makedirs(user_conversations_dir, exist_ok=True)
            conversations_dir = user_conversations_dir
        else:
            # Fallback to default location for non-authenticated users
            conversations_dir = os.path.join(os.getcwd(), 'conversations')
            os.makedirs(conversations_dir, exist_ok=True)

        file_store = LocalFileStore(conversations_dir)
        super().__init__(file_store)

    @classmethod
    async def get_instance(
        cls, config, user_id: str | None = None
    ) -> UserFileConversationStore:
        """Get instance of UserFileConversationStore"""
        return cls(user_id=user_id)
