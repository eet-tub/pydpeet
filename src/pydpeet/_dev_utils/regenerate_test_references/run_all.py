import subprocess
import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent

SCRIPTS = [
    "regenerate_read",
    "regenerate_convert",
    "regenerate_add_capacity",
    "regenerate_add_primitive_segments",
    "regenerate_add_resistance_internal",
    "regenerate_add_soc",
    "regenerate_df_primitives_correction",
    "regenerate_extract_ocv_iocv",
    "regenerate_extract_sequence_overview",
    "regenerate_filter_and_split_df_by_blocks",
    "regenerate_generate_instructions",
    "regenerate_merge_into_series",
]

python = sys.executable

for name in SCRIPTS:
    script_path = SCRIPTS_DIR / f"{name}.py"
    print(f"{'=' * 60}")
    print(f"Running: {name}...")
    print(f"{'=' * 60}")
    result = subprocess.run([python, str(script_path)], capture_output=True, text=True)
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr)
    if result.returncode != 0:
        print(f"ERROR: {name} failed with exit code {result.returncode}")
        sys.exit(1)
    else:
        print(f"Finished: {name}")
    print()

print("All reference data regenerated successfully.")
