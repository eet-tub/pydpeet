import logging
from pathlib import Path

import pandas as pd

# Required quantities of the standardized format,
# named following the BDF naming convention (preferred labels).
# Note: EIS_DC[A] has no equivalent quantity in the BDF specification.
_REQUIRED_COLUMNS_IN_BDF_NAMING_CONVENTION = [
    "Test Time / s",
    "Voltage / V",
    "Current / A",
    "Ambient Temperature / degC",
    "Step Count / 1",
    "Unix Time / s",
    "Frequency / Hz",
    "Real Impedance / ohm",
    "Imaginary Impedance / ohm",
]


def _to_dataframe(input_path: str) -> tuple[pd.DataFrame, str]:
    """
    Parses a Battery Data Format (BDF) time-series file into a pandas DataFrame.

    BDF text serialization is a delimited table whose first row contains the
    preferred BDF labels. Parquet BDF artifacts such as ``*.bdf.parquet`` are
    also accepted.

    All columns of the input file (e.g. optional BDF quantities) are kept.
    Blank columns are created for required quantities which are not present
    in the input file.

    Parameters:
        input_path (str): Path to the input file.

    Returns:
        (pd.DataFrame, str): A tuple containing the DataFrame with the data and metadata as a string.
    """
    path = Path(input_path)

    if path.suffix == ".parquet":
        df = pd.read_parquet(path)
    else:
        # Handles .bdf, .bdf.csv and .bdf.gz (compression inferred from extension).
        df = pd.read_csv(path)

    # Create blank columns for required quantities which are not present;
    # all other columns (e.g. optional BDF quantities) are kept unchanged.
    missing_columns = [col for col in _REQUIRED_COLUMNS_IN_BDF_NAMING_CONVENTION if col not in df.columns]
    if missing_columns:
        logging.warning(
            f"The following required BDF columns are missing in {input_path}: {missing_columns}. "
            "Adding them as blank columns."
        )
    for col in missing_columns:
        df[col] = None

    return df, f"BDF file: {path.name}"
