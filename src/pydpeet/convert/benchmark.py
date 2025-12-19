import os
import time
from datetime import timedelta

from pydpeet.convert.directory_standardization import directory_standardization
from pydpeet.convert.configs.config import Config, DataOutputFiletype
from pydpeet.convert.utils.timing import measure_time


def _get_directory_size(path):
    """
    Calculates the total size of all files in the given directory in megabytes (MB).

    :param path: The path to the directory to calculate the size of.
    :return: The total size of the directory in megabytes.
    """
    total_size = 0
    for dirpath, _, filenames in os.walk(path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            total_size += os.path.getsize(fp)
    return total_size / (1024 * 1024)  # Convert bytes to MB


def _ensure_empty_directory(path):
    """
    Checks if the given output directory is empty. If it is not empty, a message is printed to the console and True is returned.
    If the directory does not exist, it is created.

    :param path: The path to the directory to check.
    :return: True if the directory is not empty, False otherwise.
    """
    if os.path.exists(path) and os.listdir(path):
        print(f"ERROR: Output directory '{path}' is not empty. Please clear it before running the benchmark.")
        return True


def _format_time(seconds):
    """
    Formats the given time in seconds into a string in the format "HH:MM:SS.mmm".

    :param seconds: The time in seconds to format.
    :return: The formatted string.
    """
    td = timedelta(seconds=seconds)
    formatted_time = f"{td.seconds // 3600:02}:{(td.seconds % 3600) // 60:02}:{td.seconds % 60:02}:{td.microseconds // 1000:03}"
    return formatted_time


@measure_time
def _benchmark(input_path,
               output_path,
               config,
               keep_all_additional_data,
               data_output_filetype):
    # Ensure output directory is empty
    """
    Runs the directory standardization benchmark.

    Parameters
    ----------
    input_path : str
        The path to the directory containing the input data.
    output_path : str
        The path to the directory where the standardized data will be written.
    config : Config
        The configuration to use for standardizing the directory.
    keep_all_additional_data : bool
        Whether to keep all additional data in the output files. If False, any
        columns not specified in the configuration will be dropped.
    data_output_filetype : DataOutputFiletype
        The file type to use when exporting the data.

    Returns
    -------
    None
    """
    if _ensure_empty_directory(output_path):
        return

    # Measure input size
    input_size_mb = _get_directory_size(input_path)

    # Start timing
    start_time = time.time()

    # Run directory standardization
    directory_standardization(config=config,
                              input_path=input_path,
                              output_path=output_path,
                              keep_all_additional_data=keep_all_additional_data,
                              data_output_filetype=data_output_filetype)

    # Stop timing
    end_time = time.time()
    total_time = end_time - start_time  # in seconds

    # Measure output size
    output_size_mb = _get_directory_size(output_path)

    # Calculate compression percentage
    compression_percentage = ((input_size_mb - output_size_mb) / input_size_mb * 100) if input_size_mb > 0 else 0

    # Calculate runtime per 10GB (extrapolated)
    runtime_per_10gb_seconds = ((total_time / input_size_mb) * 1000) * 10 if input_size_mb > 0 else float('inf')

    print("\n\n=== BENCHMARK RESULTS ===")
    print(f"Config:{config}")
    print(f"Keep all Data:{keep_all_additional_data}")
    print(f"Input Data Size: {input_size_mb:.2f} MB")
    print(f"Output Data Size: {output_size_mb:.2f} MB")
    print(f"Compression: {compression_percentage:.2f}%")
    print(f"Total Runtime: {_format_time(total_time)} (hh:mm:ss:msms)")
    print(f"Estimated Runtime per 10GB: {_format_time(runtime_per_10gb_seconds)} (hh:mm:ss:msms)\n")

    return
