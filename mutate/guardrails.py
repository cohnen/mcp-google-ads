"""
Guardrails and Safety System
Provides dry-run mode, validation, and safety checks for all mutate operations
"""

import os
import logging
from typing import Dict, Any, Optional, List, Callable
from functools import wraps
import json

logger = logging.getLogger(__name__)

# Environment configuration
DRY_RUN_MODE = os.environ.get('DRY_RUN', 'false').lower() == 'true'
REQUIRE_CONFIRMATION = os.environ.get('REQUIRE_CONFIRMATION', 'true').lower() == 'true'
MAX_BUDGET_MICROS = int(os.environ.get('MAX_BUDGET_MICROS', '100000000000'))  # Default: $100,000
MAX_CAMPAIGNS_BULK = int(os.environ.get('MAX_CAMPAIGNS_BULK', '50'))  # Default: 50 campaigns


class GuardrailViolation(Exception):
    """Raised when a guardrail check fails"""
    pass


class DryRunResult:
    """Result of a dry-run operation"""

    def __init__(self, operation: str, would_execute: bool, params: Dict[str, Any], warnings: List[str] = None):
        self.operation = operation
        self.would_execute = would_execute
        self.params = self._mask_sensitive_data(params)
        self.warnings = warnings or []

    def _mask_sensitive_data(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Mask sensitive data in parameters"""
        masked = params.copy()

        # Mask customer ID (show only last 4 digits)
        if 'customer_id' in masked:
            cid = str(masked['customer_id'])
            if len(cid) > 4:
                masked['customer_id'] = f"{'*' * (len(cid) - 4)}{cid[-4:]}"

        if 'account_id' in masked:
            aid = str(masked['account_id'])
            if len(aid) > 4:
                masked['account_id'] = f"{'*' * (len(aid) - 4)}{aid[-4:]}"

        return masked

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "dry_run": True,
            "operation": self.operation,
            "would_execute": self.would_execute,
            "params": self.params,
            "warnings": self.warnings,
            "message": "This is a DRY RUN. No actual changes were made."
        }


def is_dry_run() -> bool:
    """Check if dry-run mode is enabled"""
    return DRY_RUN_MODE


def validate_budget_amount(amount_micros: int, operation: str = "budget_update") -> None:
    """
    Validate budget amount is within safe limits

    Args:
        amount_micros: Budget amount in micros
        operation: Name of operation for error message

    Raises:
        GuardrailViolation: If budget exceeds maximum
    """
    if amount_micros > MAX_BUDGET_MICROS:
        raise GuardrailViolation(
            f"{operation}: Budget {amount_micros / 1_000_000:,.2f} exceeds maximum "
            f"{MAX_BUDGET_MICROS / 1_000_000:,.2f} (set via MAX_BUDGET_MICROS env var)"
        )

    if amount_micros < 0:
        raise GuardrailViolation(f"{operation}: Budget cannot be negative")


def validate_bulk_operation(count: int, operation: str = "bulk_operation") -> None:
    """
    Validate bulk operation is within safe limits

    Args:
        count: Number of items in bulk operation
        operation: Name of operation for error message

    Raises:
        GuardrailViolation: If count exceeds maximum
    """
    if count > MAX_CAMPAIGNS_BULK:
        raise GuardrailViolation(
            f"{operation}: Operation affects {count} campaigns, "
            f"exceeds maximum {MAX_CAMPAIGNS_BULK} (set via MAX_CAMPAIGNS_BULK env var)"
        )

    if count < 1:
        raise GuardrailViolation(f"{operation}: Must affect at least 1 campaign")


def validate_roas(roas: float) -> None:
    """
    Validate ROAS value is reasonable

    Args:
        roas: Target ROAS value

    Raises:
        GuardrailViolation: If ROAS is unreasonable
    """
    if roas < 0.01:
        raise GuardrailViolation(f"ROAS {roas} is too low (minimum: 0.01)")

    if roas > 100:
        raise GuardrailViolation(f"ROAS {roas} is unreasonably high (maximum: 100)")


def check_confirmation_required(
    operation: str,
    confirm: bool,
    affected_count: Optional[int] = None
) -> None:
    """
    Check if confirmation is required for operation

    Args:
        operation: Name of operation
        confirm: Whether user confirmed
        affected_count: Number of items affected

    Raises:
        GuardrailViolation: If confirmation required but not provided
    """
    if not REQUIRE_CONFIRMATION:
        return

    # Bulk operations always require confirmation
    if affected_count and affected_count > 1 and not confirm:
        raise GuardrailViolation(
            f"{operation}: Confirmation required for bulk operation affecting {affected_count} items. "
            f"Set confirm=true to proceed."
        )


def dry_run(operation_name: str):
    """
    Decorator for dry-run mode support

    Args:
        operation_name: Name of the operation

    Returns:
        Decorated function that supports dry-run mode

    Usage:
        @dry_run("create_campaign")
        def create_campaign(...):
            # function implementation
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            if DRY_RUN_MODE:
                logger.info(f"[DRY RUN] {operation_name}: Would execute with params: {kwargs}")

                # Collect warnings
                warnings = []

                # Check budget if present
                if 'daily_budget_micros' in kwargs:
                    try:
                        validate_budget_amount(kwargs['daily_budget_micros'], operation_name)
                    except GuardrailViolation as e:
                        warnings.append(str(e))

                if 'budget_amount_micros' in kwargs:
                    try:
                        validate_budget_amount(kwargs['budget_amount_micros'], operation_name)
                    except GuardrailViolation as e:
                        warnings.append(str(e))

                # Check ROAS if present
                if 'target_roas' in kwargs and kwargs['target_roas']:
                    try:
                        validate_roas(kwargs['target_roas'])
                    except GuardrailViolation as e:
                        warnings.append(str(e))

                # Return dry-run result
                result = DryRunResult(
                    operation=operation_name,
                    would_execute=len(warnings) == 0,
                    params=kwargs,
                    warnings=warnings
                )

                return result.to_dict()

            # Normal execution
            return func(*args, **kwargs)

        return wrapper

    return decorator


def mask_sensitive_logs(log_message: str) -> str:
    """
    Mask sensitive data in log messages

    Args:
        log_message: Original log message

    Returns:
        Log message with sensitive data masked
    """
    import re

    # Mask customer IDs (10 digits)
    log_message = re.sub(r'\b(\d{6})\d{4}\b', r'\1****', log_message)

    # Mask access tokens
    log_message = re.sub(r'(Bearer\s+)[\w-]+', r'\1****', log_message)
    log_message = re.sub(r'(token["\']?\s*:\s*["\'])[\w-]+', r'\1****', log_message)

    # Mask authorization headers
    log_message = re.sub(r'(Authorization["\']?\s*:\s*["\'])[\w\s]+', r'\1****', log_message)

    return log_message


class SafeOperationContext:
    """Context manager for safe operations"""

    def __init__(self, operation: str, **kwargs):
        self.operation = operation
        self.kwargs = kwargs

    def __enter__(self):
        logger.info(f"Starting {self.operation}")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            logger.info(f"Completed {self.operation}")
        else:
            logger.error(f"Failed {self.operation}: {exc_val}")
        return False


def get_guardrail_config() -> Dict[str, Any]:
    """Get current guardrail configuration"""
    return {
        "dry_run_enabled": DRY_RUN_MODE,
        "require_confirmation": REQUIRE_CONFIRMATION,
        "max_budget_micros": MAX_BUDGET_MICROS,
        "max_budget_currency": MAX_BUDGET_MICROS / 1_000_000,
        "max_campaigns_bulk": MAX_CAMPAIGNS_BULK,
        "environment_variables": {
            "DRY_RUN": os.environ.get('DRY_RUN', 'false'),
            "REQUIRE_CONFIRMATION": os.environ.get('REQUIRE_CONFIRMATION', 'true'),
            "MAX_BUDGET_MICROS": os.environ.get('MAX_BUDGET_MICROS', '100000000000'),
            "MAX_CAMPAIGNS_BULK": os.environ.get('MAX_CAMPAIGNS_BULK', '50')
        }
    }


def check_all_guardrails(
    operation: str,
    budget_micros: Optional[int] = None,
    target_roas: Optional[float] = None,
    campaign_count: Optional[int] = None,
    confirm: bool = False
) -> List[str]:
    """
    Run all applicable guardrail checks

    Args:
        operation: Name of operation
        budget_micros: Budget amount (if applicable)
        target_roas: Target ROAS (if applicable)
        campaign_count: Number of campaigns affected (if applicable)
        confirm: Whether user confirmed

    Returns:
        List of warning messages (empty if all checks pass)

    Raises:
        GuardrailViolation: If any critical check fails
    """
    warnings = []

    # Budget validation
    if budget_micros is not None:
        try:
            validate_budget_amount(budget_micros, operation)
        except GuardrailViolation as e:
            raise e

    # ROAS validation
    if target_roas is not None:
        try:
            validate_roas(target_roas)
        except GuardrailViolation as e:
            raise e

    # Bulk operation validation
    if campaign_count is not None and campaign_count > 1:
        try:
            validate_bulk_operation(campaign_count, operation)
            check_confirmation_required(operation, confirm, campaign_count)
        except GuardrailViolation as e:
            raise e

    return warnings


# Export dry-run status for logging
logger.info(f"Guardrails initialized: DRY_RUN={DRY_RUN_MODE}, "
            f"REQUIRE_CONFIRMATION={REQUIRE_CONFIRMATION}, "
            f"MAX_BUDGET={MAX_BUDGET_MICROS / 1_000_000:,.2f}")
