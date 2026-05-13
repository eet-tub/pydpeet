# PyDPEET - Fast and Easy Battery Data Unification, Processing, and Analysis

## Contact

Feel free to open an issue on GitHub or use our email for direct enquiries: pydpeet@eet.tu-berlin.de.

<!-- ## Technical Components
alternatively: "Dependencies"
Probably not necessary? -->

## Project Goals

PyDPEET is a Python package developed to handle battery measurement data from various cyclers and other measurement devices by
* converting input data into a standardised format using Pandas data frames,
* allowing users to merge multiple single tests into test series of one cell, and multiple test series into multi-cell measurement campaigns, and
* adding sequence info either by automatically synthesising from an existing schedule or automatically analysing in case of unknown measurement procedure.

Standardised data can then be analysed using various functions which add additional data columns to a data frame:
* power, energy, capacity,
* inner resistance,
* state of charge (SOC), state of health (SOH),
* OCV points, DVA and ICA,
* and more...

Processed data can be exported to highly efficient Parquet files to be stored and re-imported later -- or to CSV or XLSX formats to maintain legacy workflows.

## Citing PyDPEET

## Documentation

![PyDPEET Workflow](docs/res/PyDPEET_Overview.svg "PyDPEET Workflow")

### GitHub Pages

* [PyDPEET homepage](https://eet-tub.github.io/pydpeet/)
* [Installation](https://eet-tub.github.io/pydpeet/installation.html)
* [API reference](https://eet-tub.github.io/pydpeet/api/index.html)
* [Examples](https://eet-tub.github.io/pydpeet/examples/index.html)
* [Developer Guide](https://eet-tub.github.io/pydpeet/developer.html)

## Installation

### For Users

Please refer to the [installation guide](https://eet-tub.github.io/pydpeet/installation.html) at our GitHub Pages.

### For Developers

Please refer to the [developer guide](https://eet-tub.github.io/pydpeet/developer.html) at our GitHub Pages.

## Current Status

## Roadmap

<!-- ## FAQ -->

## Contributing to PyDPEET

### Reporting Issues

### Request for Data Conversion

### Development Guidelines

Please refer to the [developer guide](https://eet-tub.github.io/pydpeet/developer.html) at our GitHub Pages.

<!-- ### Development Workflow -->

<!-- #### Basic Setup -->

<!-- #### Pre-Commit Hook -->

<!-- #### Autogeneration -->

<!-- #### Linting and Formatting -->