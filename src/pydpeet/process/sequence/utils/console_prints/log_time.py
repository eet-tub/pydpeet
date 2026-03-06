import logging
from contextlib import contextmanager
from time import perf_counter


@contextmanager
def log_time(
    description: str = "",
    SHOW_RUNTIME: bool = True,
):
    """
    Context manager to log the time taken by a block of code.

    The log message will show the time taken in seconds with 4 decimal places,
    and the description passed as argument.

    Parameters:
        description: str
            The description of the block of code.
        SHOW_RUNTIME: bool
            Whether to print the time taken.

    Returns:
        None
    """
    start = perf_counter()
    yield
    end = perf_counter()
    if SHOW_RUNTIME:
        logging.info(f"    {end - start:.4f}s {description}")
