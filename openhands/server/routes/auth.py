from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status

from openhands.server.services.auth_service import AuthService
from openhands.server.user_auth.user_auth import get_user_auth
from openhands.storage.data_models.user import (
    CreditTransaction,
    TokenResponse,
    UserLogin,
    UserProfile,
    UserRegistration,
    UserResponse,
)

app = APIRouter(prefix='/api/auth', tags=['authentication'])
auth_service = AuthService()

# Add a general authenticate endpoint for compatibility
authenticate_app = APIRouter(prefix='/api', tags=['authentication'])


@authenticate_app.post('/authenticate')
async def authenticate(user_auth=Depends(get_user_auth)):
    """Check if user is authenticated (for frontend compatibility)"""
    user_id = await user_auth.get_user_id()
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail='Authentication required'
        )
    return {'authenticated': True, 'user_id': user_id}


@app.post('/register', response_model=TokenResponse)
async def register(user_data: UserRegistration):
    """Register a new user"""
    return await auth_service.register_user(user_data)


@app.post('/login', response_model=TokenResponse)
async def login(login_data: UserLogin):
    """Login a user"""
    return await auth_service.login_user(login_data)


@app.get('/profile', response_model=UserResponse)
async def get_profile(user_auth=Depends(get_user_auth)):
    """Get current user's profile"""
    user_id = await user_auth.get_user_id()
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail='Authentication required'
        )

    return await auth_service.get_user_profile(user_id)


@app.put('/profile', response_model=UserResponse)
async def update_profile(profile_data: UserProfile, user_auth=Depends(get_user_auth)):
    """Update current user's profile"""
    user_id = await user_auth.get_user_id()
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail='Authentication required'
        )

    return await auth_service.update_user_profile(user_id, profile_data)


@app.get('/credits')
async def get_credits(user_auth=Depends(get_user_auth)):
    """Get current user's credit balance"""
    user_id = await user_auth.get_user_id()
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail='Authentication required'
        )

    credits = await auth_service.get_user_credits(user_id)
    return {'credits': str(credits)}


@app.get('/credits/transactions', response_model=list[CreditTransaction])
async def get_credit_transactions(user_auth=Depends(get_user_auth)):
    """Get current user's credit transaction history"""
    user_id = await user_auth.get_user_id()
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail='Authentication required'
        )

    user_store = await auth_service.get_user_store()
    return await user_store.get_credit_transactions(user_id)


@app.post('/credits/add')
async def add_credits(amount: float, user_auth=Depends(get_user_auth)):
    """Add credits to current user's account (for testing/admin purposes)"""
    user_id = await user_auth.get_user_id()
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail='Authentication required'
        )

    if amount <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail='Amount must be positive'
        )

    success = await auth_service.add_credits(user_id, amount, 'Manual credit addition')
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail='Failed to add credits',
        )

    return {'message': f'Successfully added {amount} credits'}


@app.post('/logout')
async def logout(user_auth=Depends(get_user_auth)):
    """Logout a user (invalidate token on client side)"""
    # In JWT-based auth, logout is typically handled client-side by removing the token
    # For server-side token invalidation, we would need a token blacklist
    return {'message': 'Logged out successfully'}


# Billing endpoints for compatibility with existing frontend
@app.get('/billing/credits')
async def get_billing_credits(user_auth=Depends(get_user_auth)):
    """Get current user's credit balance (billing endpoint for frontend compatibility)"""
    user_id = await user_auth.get_user_id()
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail='Authentication required'
        )

    credits = await auth_service.get_user_credits(user_id)
    return {'credits': str(credits)}


@app.post('/billing/create-customer-setup-session')
async def create_customer_setup_session(user_auth=Depends(get_user_auth)):
    """Create a customer setup session for billing (placeholder for Stripe integration)"""
    user_id = await user_auth.get_user_id()
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail='Authentication required'
        )
    
    # This is a placeholder for Stripe customer setup session creation
    # In a real implementation, you would integrate with Stripe API
    return {
        'setup_session_url': 'https://checkout.stripe.com/setup/placeholder',
        'message': 'Billing setup session created (placeholder)'
    }
