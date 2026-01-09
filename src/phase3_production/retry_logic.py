"""
Retry logic with exponential backoff for Claude API calls - FIXED for httpx

Handles transient failures gracefully:
- 429 Rate Limit
- 503 Service Unavailable  
- Network timeouts
"""
import time
import logging
from typing import Callable, Any, TypeVar, Optional
from functools import wraps

logger = logging.getLogger(__name__)

T = TypeVar('T')


class RetryConfig:
    """Configuration for retry behavior."""
    
    def __init__(
        self,
        max_attempts: int = 5,
        initial_delay: float = 1.0,
        exponential_base: float = 2.0,
        max_delay: float = 60.0,
        retryable_status_codes: tuple = (429, 503, 502, 504)
    ):
        """Initialize retry configuration."""
        self.max_attempts = max_attempts
        self.initial_delay = initial_delay
        self.exponential_base = exponential_base
        self.max_delay = max_delay
        self.retryable_status_codes = retryable_status_codes


def calculate_backoff_delay(attempt: int, config: RetryConfig) -> float:
    """Calculate exponential backoff delay."""
    delay = config.initial_delay * (config.exponential_base ** attempt)
    return min(delay, config.max_delay)


def should_retry(exception: Exception, config: RetryConfig) -> bool:
    """
    Determine if an exception should trigger a retry.
    
    CRITICAL: httpx raises HTTPStatusError, not generic exceptions.
    """
    exception_name = exception.__class__.__name__
    
    logger.info(f"Checking if should retry: {exception_name}")
    
    # CRITICAL: httpx.HTTPStatusError check
    if exception_name == 'HTTPStatusError':
        # httpx.HTTPStatusError has .response.status_code
        try:
            status_code = exception.response.status_code
            should_retry = status_code in config.retryable_status_codes
            
            if should_retry:
                logger.warning(f"🔄 Retryable HTTP error {status_code}: {str(exception)}")
            else:
                logger.error(f"❌ Non-retryable HTTP error {status_code}: {str(exception)}")
            
            return should_retry
        except AttributeError:
            logger.warning(f"HTTPStatusError without status_code: {str(exception)}")
            return False
    
    # httpx timeout exceptions
    httpx_retryable = [
        'TimeoutException',  # httpx uses this
        'ConnectTimeout',
        'ReadTimeout', 
        'WriteTimeout',
        'PoolTimeout',
        'ConnectError',
        'NetworkError',
        'RemoteProtocolError'
    ]
    
    if exception_name in httpx_retryable:
        logger.warning(f"🔄 Retryable network error: {exception_name}")
        return True
    
    # Standard Python timeout
    if exception_name == 'TimeoutError':
        logger.warning(f"🔄 Retryable timeout error")
        return True
    
    # Don't retry anything else
    logger.error(f"❌ Non-retryable error: {exception_name} - {str(exception)}")
    return False


def with_retry(config: Optional[RetryConfig] = None):
    """Decorator that adds retry logic with exponential backoff."""
    if config is None:
        config = RetryConfig()
    
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            last_exception = None
            
            for attempt in range(config.max_attempts):
                try:
                    # Attempt the function call
                    result = func(*args, **kwargs)
                    
                    # Success - log if this wasn't the first attempt
                    if attempt > 0:
                        logger.info(
                            f"✅ SUCCESS on attempt {attempt + 1}/{config.max_attempts} "
                            f"for {func.__name__}"
                        )
                    
                    return result
                    
                except Exception as e:
                    last_exception = e
                    
                    # Log the exception type for debugging
                    logger.warning(f"Caught exception: {type(e).__name__} - {str(e)[:100]}")
                    
                    # Check if we should retry
                    if not should_retry(e, config):
                        logger.error(f"❌ Non-retryable error in {func.__name__}: {str(e)[:200]}")
                        raise
                    
                    # Check if we have more attempts
                    if attempt + 1 >= config.max_attempts:
                        logger.error(
                            f"❌ Max retry attempts ({config.max_attempts}) reached "
                            f"for {func.__name__}"
                        )
                        raise
                    
                    # Calculate backoff delay
                    delay = calculate_backoff_delay(attempt, config)
                    
                    logger.warning(
                        f"🔄 Attempt {attempt + 1}/{config.max_attempts} failed for {func.__name__}. "
                        f"Retrying in {delay:.1f}s... (Error: {str(e)[:100]})"
                    )
                    
                    # Wait before retry
                    time.sleep(delay)
            
            # This should never be reached, but just in case
            if last_exception:
                raise last_exception
            
        return wrapper
    return decorator
