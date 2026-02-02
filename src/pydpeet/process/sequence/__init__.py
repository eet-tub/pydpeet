"""
Auto-generated __init__ file.
Created: 2026-02-02 10:44:50
"""

# Bind selected names from source modules into this package without leaking helper names

def _pydpeet_bind():
    import importlib, sys
    _m = importlib.import_module('pydpeet.process.sequence.utils.postprocessing.df_primitives_correction')
    globals()['df_primitives_correction'] = getattr(_m, 'df_primitives_correction')
    _m = importlib.import_module('pydpeet.process.sequence.utils.postprocessing.filter_df')
    globals()['filter_and_split_df_by_blocks'] = getattr(_m, 'filter_and_split_df_by_blocks')
    _m = importlib.import_module('pydpeet.process.sequence.utils.postprocessing.generate_instructions')
    globals()['generate_instructions'] = getattr(_m, 'generate_instructions')
    _m = importlib.import_module('pydpeet.process.sequence.step_analyzer')
    globals()['step_analyzer_primitives'] = getattr(_m, 'step_analyzer_primitives')
    globals()['step_analyzer_seqments_and_sequences'] = getattr(_m, 'step_analyzer_seqments_and_sequences')
    _m = importlib.import_module('pydpeet.process.sequence.utils.visualize.visualize_data')
    globals()['visualize_phases'] = getattr(_m, 'visualize_phases')

_pydpeet_bind()
del _pydpeet_bind

# Public API for this package
__all__ = [
    'df_primitives_correction',
    'filter_and_split_df_by_blocks',
    'generate_instructions',
    'step_analyzer_primitives',
    'step_analyzer_seqments_and_sequences',
    'visualize_phases',
]
