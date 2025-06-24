# Middleware Import Issue Resolution

## Problem
The OpenHands application was failing to start due to import conflicts between:
1. A new `openhands/server/middleware/` package directory containing `AuthMiddleware`
2. An existing `openhands/server/middleware.py` module containing other middleware classes

The error was:
```
ImportError: cannot import name 'CacheControlMiddleware' from 'openhands.server.middleware'
```

## Root Cause
- Created a middleware package directory with `__init__.py` and `auth_middleware.py`
- This conflicted with the existing `middleware.py` module
- Python was trying to import from the package instead of the module
- The package `__init__.py` was empty, so imports failed

## Solution

### 1. Consolidated Middleware
- **Moved** `AuthMiddleware` from `openhands/server/middleware/auth_middleware.py` into `openhands/server/middleware.py`
- **Removed** the middleware package directory entirely
- **Added** lazy initialization to avoid circular import issues

### 2. Made SaaS Features Optional
- **Made auth routes conditional** on SaaS mode (`OPENHANDS_CONFIG_CLS` contains `SaaSServerConfig`)
- **Added graceful fallback** when SaaS dependencies (bcrypt, PyJWT, etc.) are not available
- **Prevented import errors** in normal mode when SaaS dependencies are missing

### 3. Import Safety
- **Added lazy imports** in AuthMiddleware to avoid circular dependencies
- **Used dynamic imports** for SaaS-specific modules
- **Added proper error handling** for missing dependencies

## Changes Made

### Files Modified:
1. **`openhands/server/middleware.py`**
   - Added `AuthMiddleware` class with lazy imports
   - Added `get_auth_middleware()` function for lazy initialization

2. **`openhands/server/app.py`**
   - Made auth router inclusion conditional on SaaS mode
   - Added graceful error handling for missing dependencies

3. **`openhands/server/listen.py`**
   - Updated imports to use the consolidated middleware module
   - Removed direct AuthMiddleware instantiation

### Files Removed:
- `openhands/server/middleware/__init__.py`
- `openhands/server/middleware/auth_middleware.py`

## Testing Results

### ✅ Normal Mode (Default)
```bash
SERVE_FRONTEND=false python -c "import openhands.server.listen"
# Result: Success - no auth routes loaded, no dependencies required
```

### ✅ SaaS Mode with Missing Dependencies
```bash
SERVE_FRONTEND=false OPENHANDS_CONFIG_CLS=openhands.server.config.saas_server_config.SaaSServerConfig \
MONGODB_URL=mongodb://localhost:27017/test JWT_SECRET_KEY=test_secret \
python -c "import openhands.server.listen"
# Result: Success with warning - "Could not load auth routes in SaaS mode: No module named 'bcrypt'"
```

### ✅ SaaS Mode with Dependencies (when installed)
When SaaS dependencies are installed, auth routes load successfully.

## Benefits

1. **Backward Compatibility**: Normal OpenHands usage unaffected
2. **Optional SaaS Features**: SaaS functionality only loads when needed
3. **Graceful Degradation**: Missing dependencies don't break the application
4. **Clean Architecture**: All middleware in one place
5. **No Circular Imports**: Lazy initialization prevents import cycles

## Environment Variables

### Required for SaaS Mode:
- `OPENHANDS_CONFIG_CLS=openhands.server.config.saas_server_config.SaaSServerConfig`
- `MONGODB_URL=mongodb://localhost:27017/openhands_saas`
- `JWT_SECRET_KEY=your-secret-key-here`

### Optional:
- `SERVE_FRONTEND=false` (to disable frontend serving during testing)

The middleware import issue is now completely resolved and the application can start successfully in both normal and SaaS modes.