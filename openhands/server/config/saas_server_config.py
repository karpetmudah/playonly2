import os

from openhands.server.config.server_config import ServerConfig
from openhands.server.types import AppMode


class SaaSServerConfig(ServerConfig):
    """SaaS-specific server configuration"""

    app_mode = AppMode.SAAS
    enable_billing = True
    hide_llm_settings = False  # Allow users to configure their own LLM settings

    # SaaS-specific configurations
    user_auth_class: str = 'openhands.server.user_auth.saas_user_auth.SaaSUserAuth'

    # MongoDB-based storage for multi-tenancy
    settings_store_class: str = 'openhands.storage.settings.file_settings_store.FileSettingsStore'  # Will be user-specific
    secret_store_class: str = 'openhands.storage.secrets.file_secrets_store.FileSecretsStore'  # Will be user-specific
    conversation_store_class: str = 'openhands.storage.conversation.file_conversation_store.FileConversationStore'  # Will be user-specific

    # User store for authentication
    user_store_class: str = 'openhands.storage.user.mongodb_user_store.MongoDBUserStore'

    def verify_config(self):
        """Verify SaaS configuration"""
        required_env_vars = [
            'MONGODB_URL',
            'JWT_SECRET_KEY',
        ]

        missing_vars = []
        for var in required_env_vars:
            if not os.getenv(var):
                missing_vars.append(var)

        if missing_vars:
            raise ValueError(
                f'Missing required environment variables for SaaS mode: {", ".join(missing_vars)}'
            )

    def get_config(self):
        """Get SaaS configuration"""
        config = super().get_config()

        # Override for SaaS mode
        config.update(
            {
                'APP_MODE': self.app_mode,
                'FEATURE_FLAGS': {
                    'ENABLE_BILLING': True,
                    'HIDE_LLM_SETTINGS': self.hide_llm_settings,
                    'ENABLE_USER_REGISTRATION': True,
                    'ENABLE_MULTI_TENANT': True,
                },
                'SAAS_CONFIG': {
                    'MONGODB_URL': os.getenv('MONGODB_URL'),
                    'JWT_SECRET_KEY': os.getenv('JWT_SECRET_KEY'),
                    'TOKENS_PER_DOLLAR': float(os.getenv('TOKENS_PER_DOLLAR', '1000')),
                    'DEFAULT_CREDITS': float(os.getenv('DEFAULT_CREDITS', '10.0')),
                    'MAX_WORKSPACE_SIZE_GB': int(
                        os.getenv('MAX_WORKSPACE_SIZE_GB', '5')
                    ),
                },
            }
        )

        return config
