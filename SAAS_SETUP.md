# OpenHands SaaS Multi-Tenant Setup Guide

This guide will help you transform OpenHands into a multi-tenant SaaS application with user authentication, credit system, and workspace isolation.

## 🎯 Features

- **User Authentication**: JWT-based registration, login, and profile management
- **Credit System**: Token-based billing with automatic credit deduction
- **Workspace Isolation**: Each user gets their own isolated workspace
- **MongoDB Integration**: User data and credit transactions stored in MongoDB
- **Multi-tenant Architecture**: Secure data separation between users
- **Existing Credit System Integration**: Leverages OpenHands' existing credit infrastructure

## 🚀 Quick Start

### 1. Install Dependencies

```bash
# Run the installation script
python install_dependencies.py

# Or install manually
poetry add motor pymongo bcrypt email-validator
```

### 2. Setup MongoDB

#### Option A: Local MongoDB
```bash
# Install MongoDB locally
sudo apt-get install mongodb

# Start MongoDB
sudo systemctl start mongodb
```

#### Option B: MongoDB Atlas (Recommended for Production)
1. Create account at [MongoDB Atlas](https://cloud.mongodb.com/)
2. Create a new cluster
3. Get connection string (format: `mongodb+srv://username:password@cluster.mongodb.net/`)

### 3. Configure Environment

```bash
# Copy the SaaS environment template
cp .env.saas.example .env

# Edit .env with your configuration
nano .env
```

Required environment variables:
```env
# Application Mode
OPENHANDS_CONFIG_CLS=openhands.server.config.saas_server_config.SaaSServerConfig

# MongoDB Configuration
MONGODB_URL=mongodb://localhost:27017
# For Atlas: mongodb+srv://username:password@cluster.mongodb.net/

# JWT Authentication
JWT_SECRET_KEY=your-super-secret-jwt-key-change-this-in-production

# Credit System
TOKENS_PER_DOLLAR=1000
DEFAULT_CREDITS=10.0
```

### 4. Start the Application

```bash
# Build and run
make build && make run
```

## 🏗️ Architecture Overview

### User Authentication Flow
1. User registers with email/password
2. JWT token issued upon successful authentication
3. Token included in all API requests via Authorization header
4. Middleware validates token and extracts user ID

### Credit System
- Users start with default credits (configurable)
- Credits deducted based on token usage (configurable rate)
- Real-time credit tracking with transaction history
- Automatic session termination when credits exhausted

### Workspace Isolation
- Each user gets isolated workspace: `/workspaces/user_{user_id}/`
- User-specific settings, secrets, and conversation storage
- No cross-user data access

## 📁 File Structure

```
openhands/
├── storage/
│   ├── data_models/
│   │   └── user.py                    # User data models
│   ├── user/
│   │   └── mongodb_user_store.py      # MongoDB user storage
│   ├── settings/
│   │   └── user_file_settings_store.py # User-specific settings
│   ├── secrets/
│   │   └── user_file_secrets_store.py  # User-specific secrets
│   └── conversation/
│       └── user_file_conversation_store.py # User conversations
├── server/
│   ├── config/
│   │   └── saas_server_config.py      # SaaS configuration
│   ├── services/
│   │   ├── auth_service.py            # Authentication service
│   │   └── credit_service.py          # Credit management
│   ├── routes/
│   │   └── auth.py                    # Authentication routes
│   ├── middleware/
│   │   └── auth_middleware.py         # Auth middleware
│   └── user_auth/
│       └── saas_user_auth.py          # SaaS user auth
└── controller/
    └── credit_tracker.py              # Credit tracking integration
```

## 🔌 API Endpoints

### Authentication
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login
- `GET /api/auth/profile` - Get user profile
- `PUT /api/auth/profile` - Update user profile
- `POST /api/auth/logout` - User logout

### Credits
- `GET /api/auth/credits` - Get credit balance
- `POST /api/auth/credits/add` - Add credits (for admin/payment integration)
- `GET /api/auth/billing/credits` - Get detailed credit info

## 🔧 Configuration Options

### Credit System Configuration
```env
# Tokens per dollar (how many tokens = $1)
TOKENS_PER_DOLLAR=1000

# Default credits for new users
DEFAULT_CREDITS=10.0

# Maximum workspace size per user (GB)
MAX_WORKSPACE_SIZE_GB=5
```

### Security Configuration
```env
# JWT secret (use strong random key in production)
JWT_SECRET_KEY=your-super-secret-jwt-key

# JWT token expiration (seconds)
JWT_EXPIRATION_SECONDS=86400

# Enable billing features
ENABLE_BILLING=true
```

## 🔒 Security Features

- **Password Hashing**: bcrypt with salt
- **JWT Tokens**: Secure token-based authentication
- **Workspace Isolation**: File system level separation
- **Input Validation**: Email and password validation
- **Rate Limiting**: Built-in FastAPI rate limiting
- **CORS Protection**: Configurable CORS policies

## 💳 Payment Integration

The system is designed to integrate with payment providers:

```python
# Example Stripe integration
@router.post("/api/billing/purchase-credits")
async def purchase_credits(
    amount: float,
    payment_method_id: str,
    user_id: str = Depends(auth_middleware.require_auth)
):
    # Process payment with Stripe
    # Add credits to user account
    pass
```

## 📊 Monitoring & Analytics

### Credit Usage Tracking
- Real-time token usage monitoring
- Credit transaction history
- User activity analytics
- Cost per user tracking

### Logs
- Authentication events
- Credit transactions
- API usage patterns
- Error tracking

## 🚀 Deployment

### Docker Deployment
```dockerfile
# Add to your Dockerfile
ENV OPENHANDS_CONFIG_CLS=openhands.server.config.saas_server_config.SaaSServerConfig
ENV MONGODB_URL=mongodb+srv://user:pass@cluster.mongodb.net/
ENV JWT_SECRET_KEY=your-production-secret
```

### Environment Variables for Production
```env
# Production MongoDB
MONGODB_URL=mongodb+srv://username:password@cluster.mongodb.net/

# Strong JWT secret
JWT_SECRET_KEY=generate-strong-random-key-here

# Redis for session management
REDIS_HOST=your-redis-host
REDIS_PASSWORD=your-redis-password

# File storage
FILE_STORE=s3
FILE_STORE_PATH=s3://your-bucket
AWS_ACCESS_KEY_ID=your-key
AWS_SECRET_ACCESS_KEY=your-secret
```

## 🧪 Testing

### Run Tests
```bash
# Test authentication
pytest tests/unit/test_auth_service.py

# Test credit system
pytest tests/unit/test_credit_service.py

# Test user storage
pytest tests/unit/test_mongodb_user_store.py
```

### Manual Testing
```bash
# Register user
curl -X POST http://localhost:3000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "password123"}'

# Login
curl -X POST http://localhost:3000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "password123"}'

# Get profile (with token)
curl -X GET http://localhost:3000/api/auth/profile \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

## 🔧 Troubleshooting

### Common Issues

1. **MongoDB Connection Failed**
   - Check MongoDB URL format
   - Verify network connectivity
   - Check authentication credentials

2. **JWT Token Invalid**
   - Verify JWT_SECRET_KEY is set
   - Check token expiration
   - Ensure token format is correct

3. **Credit Deduction Not Working**
   - Check user_id is passed to AgentController
   - Verify MongoDB connection
   - Check credit service configuration

4. **Workspace Isolation Issues**
   - Verify user-specific storage classes are used
   - Check file permissions
   - Ensure workspace directories are created

### Debug Mode
```env
# Enable debug logging
LOG_LEVEL=DEBUG

# Enable detailed metrics
ENABLE_METRICS_LOGGING=true
```

## 📈 Scaling Considerations

### Database Scaling
- Use MongoDB Atlas for automatic scaling
- Implement read replicas for high traffic
- Consider sharding for large user bases

### Application Scaling
- Use Redis for session management
- Implement horizontal pod autoscaling
- Use CDN for static assets

### Storage Scaling
- Use S3 or similar for file storage
- Implement workspace cleanup policies
- Monitor storage usage per user

## 🤝 Contributing

When contributing to the SaaS features:

1. Follow existing code patterns
2. Add tests for new functionality
3. Update documentation
4. Consider security implications
5. Test with multiple users

## 📞 Support

For issues related to SaaS setup:
1. Check this documentation
2. Review logs for error messages
3. Test with minimal configuration
4. Create GitHub issue with details

---

**Note**: This SaaS transformation maintains compatibility with the existing OpenHands architecture while adding multi-tenant capabilities. Users can still run OpenHands in single-user mode by not setting the SaaS configuration.
