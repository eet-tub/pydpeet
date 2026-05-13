# API Reference

This page documents the public top-level PyDPEET API.

The functions are grouped according to a typical PyDPEET workflow:

1. Read and write battery test data
2. Process and structure sequences and primitive segments
3. Add derived quantities such as SOC, capacity, or resistance
4. Extract reduced representations and analysis data

Additional utilities and citation helpers are listed separately.

## Read and write

Functions for reading, converting, and exporting battery test data in the unified PyDPEET format.

```{eval-rst}
.. autosummary::
   :toctree: ../_autosummary
   :nosignatures:

   :caption: Read and write
   pydpeet.convert
   pydpeet.merge_into_series
   pydpeet.read
   pydpeet.write
```

## Sequence and primitive processing

Functions for detecting, correcting, filtering, and visualizing test sequences and primitive segments.

```{eval-rst}
.. autosummary::
   :toctree: ../_autosummary
   :nosignatures:

   :caption: Sequence and primitive processing
   pydpeet.add_primitive_segments
   pydpeet.df_primitives_correction
   pydpeet.extract_sequence_overview
   pydpeet.filter_and_split_df_by_blocks
   pydpeet.generate_instructions
   pydpeet.visualize_phases
```

## Add derived quantities

Functions that add derived quantities such as SOC, capacity, or resistance to existing datasets.

```{eval-rst}
.. autosummary::
   :toctree: ../_autosummary
   :nosignatures:

   :caption: Add derived quantities
   pydpeet.add_capacity
   pydpeet.add_resistance_internal
   pydpeet.add_soc
```

## Extract data

Functions for extracting OCV points, sequence summaries, and other reduced representations from datasets.

```{eval-rst}
.. autosummary::
   :toctree: ../_autosummary
   :nosignatures:

   :caption: Extract data
   pydpeet.extract_ocv_iocv
```

## Citation utilities

Utilities for handling references, citations, and BibTeX export.

```{eval-rst}
.. autosummary::
   :toctree: ../_autosummary
   :nosignatures:

   :caption: Citation utilities
   pydpeet.print_references
   pydpeet.write_to_bibtex
```

## Other

Additional public functions, classes, configurations, and utilities that do not belong to one of the main API categories.

```{eval-rst}
.. autosummary::
   :toctree: ../_autosummary
   :nosignatures:

   :caption: Other
   pydpeet.BatteryConfig
   pydpeet.SocMethod
   pydpeet.battery_config_default
   pydpeet.hakadi_nmc_1500
   pydpeet.lgm50lt_nmc_4800
   pydpeet.mapping
   pydpeet.set_logging_style
```

