# PyDPEET - Fast and Easy Battery Data Unification, Processing, and Analysis

[[_TOC_]]

## Disclaimer

This README is still under (re-)construction due to changes in the codebase.

## Description

<!-- This project enables you to convert battery measurement data to a standardized format.

Cycler output their measurement data in different formats and different file types, like for example .csv and .xslx. Each has to be handled differently which makes it difficult to work with the data and that's the reason why we created a standardized format.
The standardized Data and Metadata can be used inside of the code and can be output as a .csv (Data), .xlsx (Data) or parquet(Data) to a output_path of your choosing.

Keeping additional data outside of our definition of the standardized columns and custom cycler handling is also possible. -->


## Standardised Format

The standard columns are defined as follows:

```python
STANDARD_COLUMNS = [
    "Meta_Data",
    "Step_Count",
    "Voltage[V]",
    "Current[A]",
    "Temperature[°C]",
    "Test_Time[s]",
    "Date_Time",
    "EIS_f[Hz]",
    "EIS_Z_Real[Ohm]",
    "EIS_Z_Imag[Ohm]",
    "EIS_DC[A]"
]
```

## Meta data

## Supported Cyclers

## Installation

### For Developers

#### Rebuild package for "pip"

#### How to renew the documentation after implementing new functions

### For Users

## Usage

## Custom Handling of Cycler

## How to add a Custom Handling to the Project
