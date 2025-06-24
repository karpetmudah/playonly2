import os

import socketio

from openhands.server.app import app as base_app
from openhands.server.listen_socket import sio
from openhands.server.middleware import (  # type: ignore
    CacheControlMiddleware,
    InMemoryRateLimiter,
    LocalhostCORSMiddleware,
    RateLimitMiddleware,
    get_auth_middleware,
)
from openhands.server.static import SPAStaticFiles

if os.getenv('SERVE_FRONTEND', 'true').lower() == 'true':
    base_app.mount(
        '/', SPAStaticFiles(directory='./frontend/build', html=True), name='dist'
    )

base_app.add_middleware(LocalhostCORSMiddleware)
base_app.add_middleware(CacheControlMiddleware)
base_app.add_middleware(
    RateLimitMiddleware,
    rate_limiter=InMemoryRateLimiter(requests=10, seconds=1),
)

# Add auth middleware for SaaS mode
if os.getenv('SAAS_MODE', 'false').lower() == 'true':
    auth_middleware_instance = get_auth_middleware()
    # Note: AuthMiddleware is not a standard ASGI middleware,
    # it's used in route handlers for authentication

app = socketio.ASGIApp(sio, other_asgi_app=base_app)
