import logging
import time
from typing import Any


def measure_time(func) -> Any:
    """
    A decorator that measures the execution time of a function.

    Args:
        func (Callable): The function whose execution time is to be measured.

    Returns:
        Callable: A wrapped function that, when called, executes the original
        function and prints the time taken to execute it.
    """

    def wrapper(*args, **kwargs) -> Any:
        """
        A wrapped function that, when called, executes the original function and prints the time taken to execute it.

        Args:
            *args (Any): The arguments to be passed to the original function.
            **kwargs (Any): The keyword arguments to be passed to the original function.

        Returns:
            Any: The result of the original function.
        """
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        end_time = time.perf_counter()
        logging.info(f"{func.__name__} executed in {end_time - start_time:.6f} seconds")
        return result

    return wrapper
