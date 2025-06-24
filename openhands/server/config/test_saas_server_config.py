"""Test SaaS server configuration using in-memory storage"""

from openhands.server.config.saas_server_config import SaaSServerConfig


class TestSaaSServerConfig(SaaSServerConfig):
    """Test SaaS configuration using in-memory storage"""

    # Use memory user store for testing
    user_store_class: str = 'openhands.storage.user.memory_user_store.MemoryUserStore'