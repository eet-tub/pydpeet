import pydpeet as eet
import matplotlib.pyplot as plt

# import sys
# from pathlib import Path
# ROOT = Path(__file__).resolve().parents[4]
# sys.path.insert(0, str(ROOT))

from pathlib import Path
from tools.paths import resource_path  

p = resource_path("sample_data", "neware_sample.csv", start=Path(__file__))

# eet.convert.convert.convert_file(Config = 'Neware')

eet.convert_file(config = 'Neware', input_path = p)
