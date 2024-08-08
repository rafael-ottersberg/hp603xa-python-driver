# HP/Keysight 6033A Control

A Python driver for controlling the HP/Agilent/Keysight 6033A power supply via GPIB.

## Features

- Identify the power supply
- Set and measure voltage
- Set and measure current
- Enable/disable output
- Enable/disable foldback protection
- Read error messages

## Requirements

- Python 3.6+
- `pyvisa` library
- A GPIB interface with an installed driver (e.g. NI-VISA)

## Installation

```bash
pip install hp603xa
```

## Usage

```python
from hp603xa import Instrument

instrument = Instrument(bus='GPIB0', address=5)
instrument.identify()

instrument.set_voltage(5)
print(instrument.measure_voltage())
```
