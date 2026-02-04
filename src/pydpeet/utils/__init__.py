"""
Auto-generated __init__ file.
Created: 2026-01-30 20:07:37
"""

# Bind selected names from source modules into this package without leaking helper names

def _pydpeet_bind():
    import importlib, sys
    _m = importlib.import_module('pydpeet.utils.logging_style')
    globals()['set_logging_style'] = getattr(_m, 'set_logging_style')

_pydpeet_bind()
del _pydpeet_bind

# Public API for this package
__all__ = [
    'set_logging_style',
]
