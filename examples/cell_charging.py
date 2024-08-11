from hp603xa import Instrument
import time
import datetime


def main(logging_file=None):
    bus = "GPIB0"
    address = 5

    inst = Instrument(bus, address)
    inst.set_voltage(3.65)
    inst.set_current(30)

    while True:
        voltage = inst.measure_voltage()
        current = inst.measure_current()

        dt = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        print(f"{dt}: Voltage: {voltage:.3f} V, Current: {current:.3f} A", end="\r")
        if logging_file:
            with open(logging_file, "a") as f:
                f.write(f"{dt}, {voltage:.3f}, {current:.3f}\n")

        if current < 0.2:
            inst.disable_output()
            break

        time.sleep(1)


if __name__ == "__main__":
    main('data/cell_2_initial_charging---.csv')