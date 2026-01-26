"""
Auto-generated __init__ file.
Created: 2026-01-26 15:08:14
"""

# Bind selected names from source modules into this package without leaking helper names

def _pydpeet_bind():
    import importlib, sys
    _m = importlib.import_module('pydpeet.convert.convert')
    globals()['convert_file'] = getattr(_m, 'convert_file')
    _m = importlib.import_module('pydpeet.convert.directory_standardization')
    globals()['convert_files_in_directory'] = getattr(_m, 'convert_files_in_directory')
    _m = importlib.import_module('pydpeet.convert.export')
    globals()['export'] = getattr(_m, 'export')
    _m = importlib.import_module('pydpeet.convert.map')
    globals()['mapping'] = getattr(_m, 'mapping')

_pydpeet_bind()
del _pydpeet_bind

# Public API for this package
__all__ = [
    'convert_file',
    'convert_files_in_directory',
    'export',
    'mapping',
]
