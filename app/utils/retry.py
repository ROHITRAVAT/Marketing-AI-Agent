import asyncio
import logging
import random
from functools import wraps
from typing import Type, TypeVar, Callable, Awaitable

logger = logging.getLogger(__name__)

T = TypeVar("T")

async def retry_operation(
    operation: Callable[[], Awaitable[T]],
    max_attempts: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 10.0,
    retryable_exceptions: tuple[Type[Exception], ...] = (Exception,),
    operation_name: str = "operation"
) -> T:
    """
    Retry an asynchronous operation with exponential backoff and jitter.
    """
    attempt = 1
    delay = base_delay

    while True:
        try:
            return await operation()
        except retryable_exceptions as e:
            if attempt >= max_attempts:
                logger.warning(
                    f"{operation_name} failed after {max_attempts} attempts. "
                    f"Last error: {str(e)}"
                )
                raise

            logger.info(
                f"{operation_name} attempt {attempt} failed: {str(e)}. "
                f"Retrying in {delay:.2f} seconds..."
            )
            
            await asyncio.sleep(delay)
            
            attempt += 1
            # Exponential backoff with jitter
            delay = min(delay * 2, max_delay)
            delay = delay * (0.5 + random.random())

def with_retry(
    max_attempts: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 10.0,
    retryable_exceptions: tuple[Type[Exception], ...] = (Exception,)
):
    """
    Decorator for retrying an asynchronous function.
    """
    def decorator(func: Callable[..., Awaitable[T]]):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            async def operation():
                return await func(*args, **kwargs)
            return await retry_operation(
                operation=operation,
                max_attempts=max_attempts,
                base_delay=base_delay,
                max_delay=max_delay,
                retryable_exceptions=retryable_exceptions,
                operation_name=func.__name__
            )
        return wrapper
    return decorator
