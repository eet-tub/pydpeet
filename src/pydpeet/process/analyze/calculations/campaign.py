from pydpeet.process.analyze.calculations.add_columns import add_power, add_cumulative_energy
from pydpeet.process.analyze.calculations.capacity import add_capacity, add_soh, add_equivalent_full_cycles
from pydpeet.process.analyze.calculations.efficiency import add_coulomb_efficiency, add_internal_resistance
from pydpeet.process.analyze.calculations.soc_methods import SocMethod, add_soc
from pydpeet.process.analyze.calculations.throughput import add_charge_throughput
from pydpeet.process.analyze.calculations.utils import log_time
from pydpeet.process.analyze.configs.battery_config import BatteryConfig


# ** pipeline orchestration and builder pattern **

class Campaign:
    def __init__(self, df):
        self.df = df  # DataFrame should be passed during construction
        self.name = None
        self.config = None
        self.c_ref = None
        self.soc_start = None
        self.max_voltage = None
        self.min_voltage = None
        self.threshold_current = None
        self.voltage_interval = None
        self.steps = None
        self.verbose = True

class CampaignBuilder:
    def __init__(self, df, verbose):
        self.df = df  # Store the DataFrame in the builder
        # Initialize all attributes to None or default values
        self.name = None
        self.config = None
        self.c_ref = None
        self.soc_start = None
        self.max_voltage = None
        self.min_voltage = None
        self.threshold_current = None
        self.voltage_interval = None
        self.steps = None
        self.verbose = verbose

    # -----------------------------
    # Config setters
    # -----------------------------
    def set_df(self, df):
        self.df = df
        return self

    def set_cell_name(self, name="df"):
        self.name = name
        return self

    def set_config(self, config: BatteryConfig):
        self.config = config
        return self

    def set_c_ref(self, c_ref):
        self.c_ref = c_ref
        return self

    def set_soc_start(self, soc_start):
        self.soc_start = soc_start
        return self

    def set_max_voltage(self, max_voltage):
        self.max_voltage = max_voltage
        return self

    def set_min_voltage(self, min_voltage):
        self.min_voltage = min_voltage
        return self

    def set_threshold_current(self, threshold_current):
        self.threshold_current = threshold_current
        return self

    def set_voltage_interval(self, voltage_interval):
        self.voltage_interval = voltage_interval
        return self

    # -----------------------------
    # Analysis steps (timed + logged)
    # -----------------------------
    @log_time
    def add_power(self):
        self.df = add_power(self.df, self.verbose)
        return self

    @log_time
    def add_cumulative_energy(self):
        self.df = add_cumulative_energy(self.df, self.config, self.verbose)
        return self

    @log_time
    def add_soc(self, df_primitives,neware_bool = True, standard_method=SocMethod.WITH_RESET_WHEN_FULL_AND_EMPTY,methods=None,
                lower_soc_for_voltage=0,upper_soc_for_voltage=1,lower_voltage_for_soc=0,upper_voltage_for_soc=0,restart_for_testindex=True):

        self.df = add_soc(df=self.df,
                          df_primitives=df_primitives,
                          neware_bool=neware_bool,
                          standard_method=standard_method,
                          methods=methods,
                          config=self.config,
                          lower_soc_for_voltage=lower_soc_for_voltage,
                          upper_soc_for_voltage=upper_soc_for_voltage,
                          lower_voltage_for_soc=lower_voltage_for_soc,
                          upper_voltage_for_soc=upper_voltage_for_soc,
                          verbose=self.verbose,
                          restart_for_testindex=restart_for_testindex)
        return self

    @log_time
    def add_charge_throughput(self):
        self.df = add_charge_throughput(self.df, self.verbose)
        return self

    @log_time
    def add_coulomb_efficiency(self, df_blocks_charge, df_blocks_discharge, max_time_diff_in_secs = 300, ignore_threshold_values=False):
        self.df = add_coulomb_efficiency(self.df, df_blocks_charge, df_blocks_discharge,self.config, max_time_diff_in_secs, ignore_threshold_values,self.verbose)
        return self

    @log_time
    def add_capacity(self,neware_bool, df_primitives):
        self.df = add_capacity(self.df,neware_bool, df_primitives,self.config, self.verbose)
        return self

    @log_time
    def add_soh(self, df_primitives, neware_bool):
        self.df = add_soh(self.df,neware_bool, df_primitives, self.config, self.verbose)
        return self

    @log_time
    def add_equivalent_full_cycles(self):
        self.df = add_equivalent_full_cycles(self.df, self.config, self.verbose)
        return self

    def add_internal_resistance(self, ignore_negative_resistance_values=True):
        self.df = add_internal_resistance(self.df, self.config, self.verbose)
        return self

    # -----------------------------
    # Pipeline orchestration
    # -----------------------------
    def with_steps(self, step_methods: list):
        """
        Accepts a list of method references.
        Example: builder.with_steps([builder.add_power, builder.add_resistance])
        """
        self.steps = step_methods
        return self

    def with_all_defaults(self):
        # Choose a sensible default pipeline using method references
        self.steps = [
            self.add_power,
            self.add_soc,
            self.add_soh,
            self.add_equivalent_full_cycles,
        ]
        return self

    def build(self):
        if self.steps:
            for step in self.steps:
                step()  # Call the method reference directly
        return self.df
