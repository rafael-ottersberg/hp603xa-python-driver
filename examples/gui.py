from hp603xa import Instrument

import tkinter as tk
import math
import threading
import time

# Initialize your instrument (replace bus and address as needed)
inst = Instrument("GPIB0", 5)

# --- Gauge widget class ---
class Gauge:
    def __init__(self, parent, width=200, height=200, min_val=0, max_val=100, label="Value"):
        self.width = width
        self.height = height
        self.min_val = min_val
        self.max_val = max_val
        self.label = label

        self.canvas = tk.Canvas(parent, width=width, height=height)
        self.canvas.pack(side=tk.LEFT, padx=10, pady=10)

        # Define gauge geometry
        self.center_x = width / 2
        # Lower the center a bit to have room for the arc labels
        self.center_y = height / 2 + 20  
        self.radius = min(width, height) / 2 - 20
        self.start_angle = -135  # starting angle (in degrees)
        self.sweep_angle = 270   # total angle span

        # Draw the gauge arc (semicircular arc)
        self.canvas.create_arc(
            self.center_x - self.radius,
            self.center_y - self.radius,
            self.center_x + self.radius,
            self.center_y + self.radius,
            start=self.start_angle,
            extent=self.sweep_angle,
            style='arc',
            width=2
        )
        # Draw a needle; initially pointing to minimum value.
        self.needle = self.canvas.create_line(
            self.center_x,
            self.center_y,
            self.center_x,
            self.center_y - self.radius,
            fill="red",
            width=3
        )
        # Create a text widget to display the current value.
        self.value_text = self.canvas.create_text(
            self.center_x, 
            self.center_y + self.radius / 2,
            text=f"{self.label}: {min_val}",
            font=("Helvetica", 12)
        )

    def update(self, value):
        # Clamp value to gauge range
        if value < self.min_val:
            value = self.min_val
        if value > self.max_val:
            value = self.max_val

        # Calculate ratio and corresponding angle.
        ratio = (value - self.min_val) / (self.max_val - self.min_val)
        angle_deg = self.start_angle + ratio * self.sweep_angle
        angle_rad = math.radians(angle_deg)

        # Calculate needle endpoint
        end_x = self.center_x + self.radius * math.cos(angle_rad)
        end_y = self.center_y + self.radius * math.sin(angle_rad)
        self.canvas.coords(self.needle, self.center_x, self.center_y, end_x, end_y)

        # Update the text display.
        self.canvas.itemconfigure(self.value_text, text=f"{self.label}: {value:.2f}")

# --- Functions for instrument control ---
def set_voltage():
    try:
        voltage = float(voltage_entry.get())
        inst.set_voltage(voltage)
        # Clear the entry field after submission
        voltage_entry.delete(0, tk.END)
    except Exception as e:
        print(f"Failed to set voltage: {e}")

def set_current():
    try:
        current = float(current_entry.get())
        inst.set_current(current)
        # Clear the entry field after submission
        current_entry.delete(0, tk.END)
    except Exception as e:
        print(f"Failed to set current: {e}")

def enable_output():
    try:
        inst.enable_output()
    except Exception as e:
        print(f"Failed to enable output: {e}")

def disable_output():
    try:
        inst.disable_output()
    except Exception as e:
        print(f"Failed to disable output: {e}")

# Quick settings: set voltage and a fixed current limit of 1A.
def set_quick_setting(voltage):
    try:
        inst.set_voltage(voltage)
        inst.set_current(1.0)
    except Exception as e:
        print(f"Failed to set quick setting: {e}")

# --- UI Setup ---
root = tk.Tk()
root.title("Power Supply Control")

# --- Status Frame: display set voltage/current ---
status_frame = tk.Frame(root, padx=10, pady=10)
status_frame.pack(fill="x")
set_voltage_label = tk.Label(status_frame, text="Set Voltage: -- V", font=("Helvetica", 12))
set_voltage_label.pack(side="left", padx=(0, 20))
set_current_label = tk.Label(status_frame, text="Set Current: -- A", font=("Helvetica", 12))
set_current_label.pack(side="left", padx=(0, 20))

def update_status():
    try:
        voltage_set = inst.get_voltage()
        current_set = inst.get_current()
        set_voltage_label.config(text=f"Set Voltage: {voltage_set:.2f} V")
        set_current_label.config(text=f"Set Current: {current_set:.2f} A")
    except Exception as e:
        print(f"Error updating status: {e}")
    root.after(500, update_status)

update_status()

# --- Manual Settings Frame ---
manual_frame = tk.Frame(root, padx=10, pady=10)
manual_frame.pack(fill="x")

# Voltage controls
voltage_frame = tk.Frame(manual_frame)
voltage_frame.pack(fill="x")
voltage_label_ui = tk.Label(voltage_frame, text="Voltage (V):")
voltage_label_ui.pack(side="left")
voltage_entry = tk.Entry(voltage_frame, width=10)
voltage_entry.pack(side="left", padx=(5, 10))
voltage_set_button = tk.Button(voltage_frame, text="Set Voltage", command=set_voltage)
voltage_set_button.pack(side="left")
# Bind Enter key to set voltage
voltage_entry.bind("<Return>", lambda event: set_voltage())

# Current controls
current_frame = tk.Frame(manual_frame)
current_frame.pack(fill="x", pady=(5,0))
current_label_ui = tk.Label(current_frame, text="Current (A):")
current_label_ui.pack(side="left")
current_entry = tk.Entry(current_frame, width=10)
current_entry.pack(side="left", padx=(5, 10))
current_set_button = tk.Button(current_frame, text="Set Current", command=set_current)
current_set_button.pack(side="left")
# Bind Enter key to set current
current_entry.bind("<Return>", lambda event: set_current())

# Output control buttons
output_frame = tk.Frame(manual_frame)
output_frame.pack(fill="x", pady=(5,10))
output_enable_button = tk.Button(output_frame, text="Enable Output", command=enable_output)
output_enable_button.pack(side="left", padx=(0, 5))
output_disable_button = tk.Button(output_frame, text="Disable Output", command=disable_output)
output_disable_button.pack(side="left")

# --- Gauges Frame ---
gauges_frame = tk.Frame(root)
gauges_frame.pack()

# Create gauges:
# Adjust ranges as needed. Here we assume 0-20 V for voltage and 0-2 A for current.
voltage_gauge = Gauge(gauges_frame, width=200, height=200, min_val=0, max_val=22, label="Voltage (V)")
current_gauge = Gauge(gauges_frame, width=200, height=200, min_val=0, max_val=33, label="Current (A)")

# --- Quick Settings Frame ---
quick_frame = tk.Frame(root, padx=10, pady=10)
quick_frame.pack(fill="x")
quick_label = tk.Label(quick_frame, text="Quick Settings:")
quick_label.pack(side="left", padx=(0, 10))
quick_3v3 = tk.Button(quick_frame, text="3.3V / 1A", command=lambda: set_quick_setting(3.3))
quick_3v3.pack(side="left", padx=5)
quick_5v = tk.Button(quick_frame, text="5V / 1A", command=lambda: set_quick_setting(5))
quick_5v.pack(side="left", padx=5)
quick_12v = tk.Button(quick_frame, text="12V / 1A", command=lambda: set_quick_setting(12))
quick_12v.pack(side="left", padx=5)

# --- Function to update gauges periodically ---
def update_gauges():
    try:
        measured_voltage = inst.measure_voltage()
        measured_current = inst.measure_current()
        voltage_gauge.update(measured_voltage)
        current_gauge.update(measured_current)
    except Exception as e:
        print(f"Error updating gauges: {e}")
    root.after(500, update_gauges)

# Start updating the gauges.
update_gauges()

# Run the main application loop
root.mainloop()
