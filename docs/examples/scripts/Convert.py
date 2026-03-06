import pydpeet as eet

eet.utils.set_logging_style(level="INFO", formatting_string="%(levelname)s | %(pathname)s:%(lineno)d | %(message)s")

Data = eet.read(config="Neware_", input_path=r"..\..\res\raw\Cal_Ageing_Checkup1.xlsx")
