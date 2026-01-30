"""
Auto-generated __init__ file.
Created: 2026-01-26 15:08:14
"""

# Bind selected names from source modules into this package without leaking helper names

def _pydpeet_bind():
    import importlib, sys
    _m = importlib.import_module('pydpeet.process.analyze.calculations.soc_methods')
    globals()['SocMethod'] = getattr(_m, 'SocMethod')
    globals()['add_soc'] = getattr(_m, 'add_soc')
    _m = importlib.import_module('pydpeet.process.analyze.calculations.capacity')
    globals()['add_capacity'] = getattr(_m, 'add_capacity')
    _m = importlib.import_module('pydpeet.process.analyze.calculations.efficiency')
    globals()['add_internal_resistance'] = getattr(_m, 'add_internal_resistance')
    _m = importlib.import_module('pydpeet.process.analyze.configs.battery_config')
    globals()['am23nmc'] = getattr(_m, 'am23nmc')
    globals()['battery_default'] = getattr(_m, 'battery_default')
    globals()['BatteryConfig'] = getattr(_m, 'BatteryConfig')
    globals()['tc23nmc'] = getattr(_m, 'tc23nmc')
    _m = importlib.import_module('pydpeet.process.analyze.extract.OCV.iocv_detection')
    globals()['iocv_detection'] = getattr(_m, 'iocv_detection')

_pydpeet_bind()
del _pydpeet_bind

# Public API for this package
__all__ = [
    'SocMethod',
    'add_capacity',
    'add_internal_resistance',
    'add_soc',
    'am23nmc',
    'battery_default',
    'iocv_detection',
    'tc23nmc',
]
