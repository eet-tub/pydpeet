from .convert import convert
from .configs.config import Config

class _ConvertAPI:
    def __call__(self, *args, **kwargs):
        return convert(*args, **kwargs)

    # class Config:
    #     Neware = NewareConfig

# ersetze das Modul durch die API
import sys
sys.modules[__name__] = _ConvertAPI()