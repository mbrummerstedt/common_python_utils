import os
from dotenv import load_dotenv
from functools import wraps
import time

from set_structlog_configs import get_logger

# ==============================================================================
# Set variables and authenticate
# ==============================================================================

load_dotenv()
ENV = os.getenv("ENV", "dev")  # Default to 'dev' if not set

log = get_logger(__name__, env=ENV)

# ==============================================================================
# Time a function
# ==============================================================================

def timeit(func):
    @wraps(func)
    def timeit_wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        end_time = time.perf_counter()
        total_time = end_time - start_time
        # first item in the args, ie `args[0]` is `self`
        log.info(f'Function {func.__name__} Took {total_time:.4f} seconds')
        return result
    return timeit_wrapper