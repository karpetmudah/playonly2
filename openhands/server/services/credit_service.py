from __future__ import annotations

import os

from openhands.core.logger import openhands_logger as logger
from openhands.server.services.auth_service import AuthService


class CreditService:
    """Service for managing credit deductions based on token usage"""

    def __init__(self):
        self.auth_service = AuthService()
        # Default rate: $0.01 per 1000 tokens (configurable via environment)
        self.tokens_per_dollar = float(os.getenv('TOKENS_PER_DOLLAR', '1000'))

    def calculate_cost(self, token_count: int) -> float:
        """Calculate cost in dollars based on token count"""
        return token_count / self.tokens_per_dollar

    async def deduct_credits_for_tokens(
        self,
        user_id: str,
        token_count: int,
        task_description: str = 'AI task execution',
        model_name: str | None = None,
    ) -> bool:
        """Deduct credits based on token usage"""
        if token_count <= 0:
            return True  # No tokens used, no deduction needed

        cost = self.calculate_cost(token_count)

        metadata = {
            'token_count': token_count,
            'model_name': model_name,
            'cost_per_token': 1 / self.tokens_per_dollar,
            'task_type': 'ai_execution',
        }

        description = f'{task_description} ({token_count} tokens, {model_name or "unknown model"})'

        success = await self.auth_service.deduct_credits(
            user_id=user_id, amount=cost, description=description, metadata=metadata
        )

        if success:
            logger.info(
                f'Deducted ${cost:.4f} ({token_count} tokens) from user {user_id}'
            )
        else:
            logger.warning(
                f'Failed to deduct credits from user {user_id} - insufficient balance'
            )

        return success

    async def check_sufficient_credits(
        self, user_id: str, estimated_tokens: int
    ) -> bool:
        """Check if user has sufficient credits for estimated token usage"""
        estimated_cost = self.calculate_cost(estimated_tokens)
        current_credits = await self.auth_service.get_user_credits(user_id)

        return current_credits >= estimated_cost

    async def get_token_allowance(self, user_id: str) -> int:
        """Get maximum tokens user can afford with current credits"""
        current_credits = await self.auth_service.get_user_credits(user_id)
        return int(current_credits * self.tokens_per_dollar)
