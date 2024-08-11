import pyvisa

class Instrument:
    def __init__(self, bus, gpib_address):
        self.gpib_address = gpib_address
        self.bus = bus
        self.rm = pyvisa.ResourceManager()
        self.gpib_instrument = self.rm.open_resource(
            f"{self.bus}::{gpib_address}")
        # Set the language to TMSL (SCPI)
        self.gpib_instrument.write('SYST:LANG TMSL')
        assert self.gpib_instrument.query(
            'SYST:LANG?') == 'TMSL\n', "Set language to TMSL/SCPI failed."

    def parse_number(self, number_string):
        return float(number_string.strip('\n'))

    def identify(self):
        return self.gpib_instrument.query("*IDN?").strip('\n')

    def enable_foldback(self):
        """Enable the foldback protection of the power supply."""
        self.gpib_instrument.write("CURR:PROT:FOLD ON")
        assert self.gpib_instrument.query(
            "CURR:PROT:FOLD?") == "1\n", "Enable foldback failed."

    def disable_foldback(self):
        """Disable the foldback protection of the power supply."""
        self.gpib_instrument.write("CURR:PROT:FOLD OFF")
        assert self.gpib_instrument.query(
            "CURR:PROT:FOLD?") == "0\n", "Disable foldback failed."

    def enable_output(self):
        """Enable the output of the power supply."""
        self.gpib_instrument.write("OUTP:STAT ON")
        assert self.gpib_instrument.query(
            "OUTP:STAT?") == "1\n", "Enable output failed."

    def disable_output(self):
        """Disable the output of the power supply."""
        self.gpib_instrument.write("OUTP:STAT OFF")
        assert self.gpib_instrument.query(
            "OUTP:STAT?") == "0\n", "Disable output failed."

    def read_errors(self):
        """Read the error message of the power supply."""
        errors = []
        while True:
            error = self.gpib_instrument.query("SYST:ERR?")
            if error == '+0,"No error"\n':
                break
            errors.append(error.strip('\n'))
        return errors

    def set_voltage(self, voltage):
        """Set the output voltage of the power supply with unit [V]."""
        try:
            self.gpib_instrument.write(f"SOUR:VOLT {voltage}")

            voltage_set = self.parse_number(
                self.gpib_instrument.query("SOUR:VOLT?"))
            assert voltage_set == voltage, f"Set voltage {voltage}V failed, got {voltage_set} V."
        except Exception as e:
            print(e)
            print(self.read_errors())

    def set_current(self, current):
        """Set the output current of the power supply with unit [A]."""
        try:
            self.gpib_instrument.write(f"SOUR:CURR {current}")

            current_set = self.parse_number(
                self.gpib_instrument.query("SOUR:CURR?"))
            assert current_set == current, f"Set current {current}A failed, got {current_set} A."
        except Exception as e:
            print(e)
            print(self.read_errors())

    def get_current(self):
        """Get the output current setting of the power supply with unit [A]."""
        return self.parse_number(self.gpib_instrument.query("SOUR:CURR?"))
    
    def get_voltage(self):
        """Get the output voltage setting of the power supply with unit [V]."""
        return self.parse_number(self.gpib_instrument.query("SOUR:VOLT?"))

    def measure_voltage(self):
        """Measure the output voltage of the power supply with unit [V]."""
        return self.parse_number(self.gpib_instrument.query("MEAS:VOLT?"))

    def measure_current(self):
        """Measure the output current of the power supply with unit [A]."""
        return self.parse_number(self.gpib_instrument.query("MEAS:CURR?"))


if __name__ == "__main__":
    inst = Instrument("GPIB0", 5)
    print(inst.identify())
