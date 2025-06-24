# OpenHands SaaS Transformation Guide

## 🎯 Overview

This guide documents the complete transformation of OpenHands into a multi-tenant SaaS application with user authentication, credit-based billing, and workspace isolation.

## ✅ Completed Features

### 🔐 Authentication System
- **User Registration**: Email/password registration with JWT token generation
- **User Login**: Secure authentication with JWT token response
- **Token Validation**: `/api/authenticate` endpoint for session verification
- **Frontend Integration**: Complete auth flow with login/register forms

### 💳 Billing & Credits System
- **Credit Management**: User credit tracking and deduction
- **Token-based Billing**: Credits deducted based on AI API token usage
- **Billing API**: `/api/auth/billing/credits` endpoint for credit queries

### 🏗️ Architecture Improvements
- **Memory User Store**: Testing implementation without MongoDB dependency
- **Configurable Storage**: Easy switch between memory and MongoDB storage
- **JWT Security**: Secure token-based session management
- **Multi-tenant Ready**: User workspace isolation without separate Docker containers

## 🚀 Quick Start

### 1. Start the SaaS Backend
```bash
cd /workspace/playonly
export SAAS_MODE=true
export USER_STORE_CLASS=MemoryUserStore  # For testing
# export USER_STORE_CLASS=MongoUserStore  # For production
# export MONGODB_URI=mongodb://localhost:27017/openhands  # For production
python -m openhands.server.app
```

### 2. Start the Frontend
```bash
cd frontend
npm install
npm run dev -- --host 0.0.0.0 --port 12000
```

### 3. Access the Application
- **Main App**: http://localhost:12000
- **Auth Page**: http://localhost:12000/auth (auto-redirect for unauthenticated users)
- **API Docs**: http://localhost:8000/docs

## 🔧 API Endpoints

### Authentication Endpoints

#### Register User
```bash
POST /api/auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securepassword",
  "full_name": "John Doe"  # optional
}

Response:
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "user": {
    "user_id": "uuid-here",
    "email": "user@example.com",
    "full_name": "John Doe",
    "credits": "100.0"
  }
}
```

#### Login User
```bash
POST /api/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securepassword"
}

Response:
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "user": {
    "user_id": "uuid-here",
    "email": "user@example.com",
    "full_name": "John Doe",
    "credits": "100.0"
  }
}
```

#### Authenticate Token
```bash
POST /api/authenticate
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...

Response:
{
  "authenticated": true,
  "user_id": "uuid-here"
}
```

#### Get User Credits
```bash
GET /api/auth/billing/credits
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...

Response:
{
  "credits": "95.50"
}
```

## 🏗️ Technical Implementation

### Backend Changes

#### 1. Authentication Router (`openhands/server/routes/auth.py`)
- Added `/authenticate` endpoint for token validation
- Integrated with existing billing and user management
- Proper error handling and security

#### 2. User Storage (`openhands/storage/user/`)
- **MemoryUserStore**: In-memory storage for testing
- **MongoUserStore**: MongoDB storage for production
- Configurable via `USER_STORE_CLASS` environment variable

#### 3. Server Configuration
- **TestSaaSServerConfig**: Development configuration with memory storage
- **SaaSServerConfig**: Production configuration with MongoDB
- Environment-based configuration switching

#### 4. Data Models (`openhands/storage/data_models/`)
- Fixed User model field mapping (`user_id`, `transaction_id`)
- Added proper transaction type handling
- Credit management integration

### Frontend Changes

#### 1. Routing (`frontend/src/routes.ts`)
- Added `/auth` route for authentication page
- Integrated with existing routing system

#### 2. Authentication Flow (`frontend/src/routes/root-layout.tsx`)
- SaaS mode detection and redirect logic
- Automatic redirect to `/auth` for unauthenticated users
- Preserved existing OAuth flow for non-SaaS mode

#### 3. Auth Components (`frontend/src/components/features/auth/`)
- **LoginForm**: Complete login form with validation
- **RegisterForm**: Registration form with password confirmation
- **AuthPage**: Main authentication page with form switching

#### 4. Internationalization (`frontend/src/i18n/`)
- Added comprehensive AUTH translation keys
- Support for login/register form labels and messages
- Error handling translations

#### 5. API Integration (`frontend/src/api/`)
- JWT token handling in axios interceptors
- Automatic token storage and retrieval
- Error handling for authentication failures

## 🔒 Security Features

### JWT Token Security
- **HS256 Algorithm**: Secure token signing
- **Expiration**: 7-day token expiration
- **Validation**: Comprehensive token validation on each request

### Password Security
- **Bcrypt Hashing**: Secure password hashing with salt
- **Minimum Length**: 8-character minimum password requirement
- **Validation**: Client and server-side password validation

### API Security
- **Authentication Required**: All protected endpoints require valid JWT
- **Error Handling**: Secure error messages without information leakage
- **CORS Configuration**: Proper CORS setup for frontend integration

## 💰 Credit System

### Credit Deduction Logic
- **Token-based Billing**: Credits deducted based on AI API token usage
- **Configurable Rates**: Easy adjustment of credit-to-token ratios
- **Real-time Tracking**: Immediate credit updates after API calls

### Credit Management
- **Initial Credits**: New users start with 100 credits
- **Credit Queries**: Real-time credit balance checking
- **Top-up Ready**: Infrastructure ready for credit purchase integration

## 🚀 Production Deployment

### Environment Variables
```bash
# Required for SaaS mode
export SAAS_MODE=true
export USER_STORE_CLASS=MongoUserStore
export MONGODB_URI=mongodb://your-mongodb-server:27017/openhands
export JWT_SECRET=your-super-secret-jwt-key

# Optional configurations
export JWT_EXPIRATION_DAYS=7
export DEFAULT_USER_CREDITS=100.0
```

### MongoDB Setup
1. Install and configure MongoDB
2. Create database: `openhands`
3. Collections will be created automatically
4. Ensure proper indexing for performance

### Frontend Configuration
```bash
# frontend/.env
VITE_BACKEND_BASE_URL="your-backend-domain.com"
VITE_BACKEND_HOST="your-backend-domain.com"
VITE_MOCK_API="false"
VITE_MOCK_SAAS="false"
VITE_USE_TLS="true"
```

## 🧪 Testing

### Backend Testing
```bash
# Test user registration
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"testpass123"}'

# Test user login
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"testpass123"}'

# Test token authentication
curl -X POST http://localhost:8000/api/authenticate \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# Test credit balance
curl -X GET http://localhost:8000/api/auth/billing/credits \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### Frontend Testing
1. Navigate to http://localhost:12000
2. Should redirect to `/auth` if not authenticated
3. Test registration and login flows
4. Verify token storage and automatic authentication

## 🔄 Migration from Existing Installation

### For Development
1. Set `SAAS_MODE=true` in environment
2. Use `MemoryUserStore` for quick testing
3. Existing data remains unchanged

### For Production
1. Set up MongoDB database
2. Configure `MongoUserStore` and `MONGODB_URI`
3. Migrate existing user data if needed
4. Update frontend configuration

## 🛠️ Troubleshooting

### Common Issues

#### 1. Authentication Errors
- **Issue**: 401 Unauthorized responses
- **Solution**: Check JWT token validity and expiration
- **Debug**: Verify `JWT_SECRET` matches between registration and validation

#### 2. Database Connection
- **Issue**: MongoDB connection failures
- **Solution**: Verify `MONGODB_URI` and database accessibility
- **Debug**: Check MongoDB logs and network connectivity

#### 3. Frontend Redirect Issues
- **Issue**: Not redirecting to auth page
- **Solution**: Verify `VITE_MOCK_SAAS` is set correctly
- **Debug**: Check browser console for routing errors

#### 4. Credit Deduction
- **Issue**: Credits not being deducted
- **Solution**: Verify credit system integration in agent workflows
- **Debug**: Check transaction logs and credit calculation logic

## 📈 Future Enhancements

### Planned Features
- **Payment Integration**: Stripe/PayPal integration for credit purchases
- **Usage Analytics**: Detailed usage tracking and reporting
- **Team Management**: Multi-user team accounts and permissions
- **API Rate Limiting**: Request rate limiting per user/plan
- **Advanced Billing**: Subscription plans and usage tiers

### Scalability Improvements
- **Database Optimization**: Indexing and query optimization
- **Caching Layer**: Redis integration for session management
- **Load Balancing**: Multi-instance deployment support
- **Monitoring**: Comprehensive logging and metrics

## 📞 Support

For issues or questions regarding the SaaS transformation:
1. Check this documentation first
2. Review the test results in the commit messages
3. Examine the implementation in the codebase
4. Test with the provided API examples

## 🎉 Success Metrics

### ✅ Completed Objectives
- ✅ Multi-tenant user authentication system
- ✅ Credit-based billing integration
- ✅ Secure JWT token management
- ✅ Frontend authentication flow
- ✅ User workspace isolation
- ✅ MongoDB integration ready
- ✅ Production deployment ready
- ✅ Comprehensive testing completed

### 🚀 Ready for Launch
The OpenHands SaaS transformation is complete and ready for production deployment. All authentication endpoints are functional, the frontend provides a seamless user experience, and the credit system is integrated and operational.