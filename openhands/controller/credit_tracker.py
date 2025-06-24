from __future__ import annotations

import os
from typing import TYPE_CHECKING

from openhands.core.logger import openhands_logger as logger
from openhands.llm.metrics import TokenUsage

if TYPE_CHECKING:
    from openhands.server.services.credit_service import CreditService


class CreditTracker:
    """Tracks and deducts credits based on token usage for SaaS mode"""

    def __init__(self, user_id: str | None = None):
        self.user_id = user_id
        self.credit_service: CreditService | None = None
        self.is_saas_mode = os.getenv('OPENHANDS_CONFIG_CLS', '').endswith(
            'SaaSServerConfig'
        )
        self.total_tokens_used = 0
        self.total_cost_deducted = 0.0

        # Lazy initialization of credit service to avoid circular imports
        if user_id and self.is_saas_mode:
            self._init_credit_service()

    def _init_credit_service(self) -> None:
        """Lazy initialization of credit service to avoid circular imports"""
        try:
            from openhands.server.services.credit_service import CreditService

            self.credit_service = CreditService()
        except ImportError as e:
            logger.warning(f'Could not initialize credit service: {e}')
            self.credit_service = None

    async def track_token_usage(
        self,
        token_usage: TokenUsage,
        model_name: str | None = None,
        task_description: str = 'AI task execution',
    ) -> bool:
        """
        Track token usage and deduct credits if in SaaS mode

        Returns:
            bool: True if credits were successfully deducted or not needed, False if insufficient credits
        """
        if not self.is_saas_mode or not self.user_id or not self.credit_service:
            # Not in SaaS mode or no user, no credit deduction needed
            return True

        # Calculate total tokens used in this call
        total_tokens = (
            token_usage.prompt_tokens
            + token_usage.completion_tokens
            + getattr(token_usage, 'cache_read_tokens', 0)
            + getattr(token_usage, 'cache_write_tokens', 0)
        )

        if total_tokens <= 0:
            return True  # No tokens used, no deduction needed

        try:
            success = await self.credit_service.deduct_credits_for_tokens(
                user_id=self.user_id,
                token_count=total_tokens,
                task_description=task_description,
                model_name=model_name,
            )

            if success:
                self.total_tokens_used += total_tokens
                cost = self.credit_service.calculate_cost(total_tokens)
                self.total_cost_deducted += cost
                logger.info(
                    f'Credit deduction successful: {total_tokens} tokens, ${cost:.4f} '
                    f'(Total session: {self.total_tokens_used} tokens, ${self.total_cost_deducted:.4f})'
                )
            else:
                logger.warning(
                    f'Credit deduction failed for user {self.user_id}: insufficient credits '
                    f'for {total_tokens} tokens'
                )

            return success

        except Exception as e:
            logger.error(f'Error during credit deduction: {e}')
            return False

    async def check_sufficient_credits(self, estimated_tokens: int) -> bool:
        """Check if user has sufficient credits for estimated token usage"""
        if not self.is_saas_mode or not self.user_id or not self.credit_service:
            return True

        try:
            return await self.credit_service.check_sufficient_credits(
                self.user_id, estimated_tokens
            )
        except Exception as e:
            logger.error(f'Error checking credit balance: {e}')
            return False

    async def get_remaining_token_allowance(self) -> int:
        """Get the maximum tokens user can afford with current credits"""
        if not self.is_saas_mode or not self.user_id or not self.credit_service:
            return 999999999  # Very large number for non-SaaS mode

        try:
            return await self.credit_service.get_token_allowance(self.user_id)
        except Exception as e:
            logger.error(f'Error getting token allowance: {e}')
            return 0

    def get_session_summary(self) -> dict:
        """Get summary of credit usage for this session"""
        return {
            'total_tokens_used': self.total_tokens_used,
            'total_cost_deducted': self.total_cost_deducted,
            'user_id': self.user_id,
            'is_saas_mode': self.is_saas_mode,
        }
