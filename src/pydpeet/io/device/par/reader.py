import logging
from io import StringIO

import pandas as pd

from pydpeet.utils.guardrails import _guardrail_empty_file


def _to_dataframe(input_path: str) -> tuple[pd.DataFrame, str]:
    """
    Parses the input file from the VersaStudio PAR cycler into a pandas DataFrame.

    Parameters:
    input_path (str): Path to the input file.

    Returns:
    (pandas.DataFrame, str): A tuple containing the DataFrame with data and metadata as a string.
    """
    _guardrail_empty_file(input_path)

    metadata_lines: list[str] = []
    csv_lines: list[str] = []
    in_segment = False

    with open(input_path, encoding="utf-8-sig") as file:
        for raw_line in file:
            line = raw_line.strip()
            if not line:
                continue
            if line.startswith("<Segment"):
                in_segment = True
                continue
            if line.startswith("</Segment"):
                in_segment = False
                continue
            if in_segment:
                if line.startswith("Definition="):
                    columns = [column.strip() for column in line.split("=", 1)[1].split(",")]
                    columns.pop()
                    if not csv_lines:
                        csv_lines.append(",".join(columns))
                elif "=" not in line:
                    csv_lines.append(line)
            else:
                metadata_lines.append(line)

    metadata = "\n".join(metadata_lines)
    if not csv_lines:
        logging.warning("No segment data found in %s", input_path)
        return pd.DataFrame(), metadata

    return pd.read_csv(StringIO("\n".join(csv_lines))), metadata
