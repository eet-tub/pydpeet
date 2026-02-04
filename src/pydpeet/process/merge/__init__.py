"""
Auto-generated __init__ file.
Created: 2026-01-30 20:07:37
"""

# Bind selected names from source modules into this package without leaking helper names

def _pydpeet_bind():
    import importlib, sys
    _m = importlib.import_module('pydpeet.process.merge.series')
    globals()['run_series'] = getattr(_m, 'run_series')

_pydpeet_bind()
del _pydpeet_bind

# Public API for this package
__all__ = [
    'run_series',
]
