"""
Auto-generated __init__ file.
Created: 2026-02-02 10:44:50
"""

# Bind selected names from source modules into this package without leaking helper names

def _pydpeet_bind():
    import importlib, sys
    _m = importlib.import_module('pydpeet.citations.citeme')
    globals()['print_references'] = getattr(_m, 'print_references')
    globals()['write_to_bibtex'] = getattr(_m, 'write_to_bibtex')

_pydpeet_bind()
del _pydpeet_bind

# Public API for this package
__all__ = [
    'print_references',
    'write_to_bibtex',
]
