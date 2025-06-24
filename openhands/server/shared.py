import os

import socketio
from dotenv import load_dotenv

from openhands.core.config import load_openhands_config
from openhands.core.config.openhands_config import OpenHandsConfig
from openhands.server.config.server_config import ServerConfig, load_server_config
from openhands.server.conversation_manager.conversation_manager import (
    ConversationManager,
)
from openhands.server.monitoring import MonitoringListener
from openhands.server.types import ServerConfigInterface
from openhands.storage import get_file_store
from openhands.storage.conversation.conversation_store import ConversationStore
from openhands.storage.files import FileStore
from openhands.storage.secrets.secrets_store import SecretsStore
from openhands.storage.settings.settings_store import SettingsStore
from openhands.utils.import_utils import get_impl

load_dotenv()

config: OpenHandsConfig = load_openhands_config()
server_config_interface: ServerConfigInterface = load_server_config()
assert isinstance(server_config_interface, ServerConfig), (
    'Loaded server config interface is not a ServerConfig, despite this being assumed'
)
server_config: ServerConfig = server_config_interface
file_store: FileStore = get_file_store(
    config.file_store,
    config.file_store_path,
    config.file_store_web_hook_url,
    config.file_store_web_hook_headers,
)

client_manager = None
redis_host = os.environ.get('REDIS_HOST')
if redis_host:
    client_manager = socketio.AsyncRedisManager(
        f'redis://{redis_host}',
        redis_options={'password': os.environ.get('REDIS_PASSWORD')},
    )


sio = socketio.AsyncServer(
    async_mode='asgi', cors_allowed_origins='*', client_manager=client_manager
)

MonitoringListenerImpl = get_impl(
    MonitoringListener,
    server_config.monitoring_listener_class,
)

monitoring_listener = MonitoringListenerImpl.get_instance(config)

ConversationManagerImpl = get_impl(
    ConversationManager,
    server_config.conversation_manager_class,
)

conversation_manager = ConversationManagerImpl.get_instance(
    sio, config, file_store, server_config, monitoring_listener
)

# For SaaS mode, we use user-specific store implementations
if hasattr(server_config, 'app_mode') and server_config.app_mode.value == 'saas':
    from openhands.storage.conversation.user_file_conversation_store import (
        UserFileConversationStore,
    )
    from openhands.storage.secrets.user_file_secrets_store import UserFileSecretsStore
    from openhands.storage.settings.user_file_settings_store import (
        UserFileSettingsStore,
    )

    SettingsStoreImpl: type[SettingsStore] = UserFileSettingsStore  # type: ignore
    SecretsStoreImpl: type[SecretsStore] = UserFileSecretsStore  # type: ignore
    ConversationStoreImpl: type[ConversationStore] = UserFileConversationStore  # type: ignore
else:
    SettingsStoreImpl = get_impl(SettingsStore, server_config.settings_store_class)
    SecretsStoreImpl = get_impl(SecretsStore, server_config.secret_store_class)
    ConversationStoreImpl = get_impl(
        ConversationStore,
        server_config.conversation_store_class,
    )
