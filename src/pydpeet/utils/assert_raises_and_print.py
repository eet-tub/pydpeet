import pytest


def assert_raises_and_print(exc_type, func, **kwargs):
    """Executes a function, asserts it raises an exception, and prints the error message."""
    with pytest.raises(exc_type) as excinfo:
        func(**kwargs)
    print(f"\nCaptured {exc_type.__name__}: {excinfo.value}")
