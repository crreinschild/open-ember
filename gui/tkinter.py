import tkinter as tk
from tkinter import simpledialog
from ember import bluetooth
import asyncio

class Window(tk.Tk):
    ember = bluetooth.Ember()

    def __init__(self, loop):
        self.loop = loop
        self.root = tk.Tk()
        battery_percentage_label = tk.Label(text="Battery Percentage")
        battery_percentage_label.grid(row=0, column=0, padx=(10,10), pady=(10, 10))
        self.battery_percentage_value = tk.Label(text="0")
        self.battery_percentage_value.grid(row=0, column=1, padx=(10,10), pady=(10, 10))
        charging_status_label = tk.Label(text="Charging Status")
        charging_status_label.grid(row=1, column=0, padx=(10,10), pady=(10, 10))
        self.charging_status_value = tk.Label(text="0")
        self.charging_status_value.grid(row=1, column=1, padx=(10,10), pady=(10, 10))
        battery_temperature_label = tk.Label(text="Battery Temperature")
        battery_temperature_label.grid(row=2, column=0, padx=(10,10), pady=(10, 10))
        self.battery_temperature_value = tk.Label(text="0")
        self.battery_temperature_value.grid(row=2, column=1, padx=(10,10), pady=(10, 10))
        battery_voltage_maybe_label = tk.Label(text="Battery Voltage Maybe")
        battery_voltage_maybe_label.grid(row=3, column=0, padx=(10,10), pady=(10, 10))
        self.battery_voltage_maybe_value = tk.Label(text="0")
        self.battery_voltage_maybe_value.grid(row=3, column=1, padx=(10,10), pady=(10, 10))
        current_temperature_label = tk.Label(text="Current Temperature")
        current_temperature_label.grid(row=4, column=0, padx=(10,10), pady=(10, 10))
        self.current_temperature_value = tk.Label(text="0")
        self.current_temperature_value.grid(row=4, column=1, padx=(10,10), pady=(10, 10))
        liquid_level_label = tk.Label(text="Liquid Level")
        liquid_level_label.grid(row=5, column=0, padx=(10,10), pady=(10, 10))
        self.liquid_level_value = tk.Label(text="0")
        self.liquid_level_value.grid(row=5, column=1, padx=(10,10), pady=(10, 10))
        liquid_state_label = tk.Label(text="Liquid State")
        liquid_state_label.grid(row=6, column=0, padx=(10,10), pady=(10, 10))
        self.liquid_state_value = tk.Label(text="0")
        self.liquid_state_value.grid(row=6, column=1, padx=(10,10), pady=(10, 10))
        target_temperature_label = tk.Label(text="Target Temperature")
        target_temperature_label.grid(row=8, column=0, padx=(10,10), pady=(10, 10))
        self.target_temperature_value = tk.Label(text="0")
        self.target_temperature_value.grid(row=8, column=1, padx=(10,10), pady=(10, 10))
        charging_state_label = tk.Label(text="Charging State")
        charging_state_label.grid(row=9, column=0, padx=(10,10), pady=(10, 10))
        self.charging_state_value = tk.Label(text="0")
        self.charging_state_value.grid(row=9, column=1, padx=(10,10), pady=(10, 10))
        set_temperature_button = tk.Button(text="Set Temperature", command=self.set_temperature)
        set_temperature_button.grid(row=10, column=0, padx=(10,10), pady=(10, 10))
        button = tk.Button(text="Close", command=self.close)
        button.grid(row=11, column=0, padx=(10,10), pady=(10, 10))

    def set_temperature(self):
        choice = simpledialog.askfloat("Choose Temperature", "Choose Temperature, 0 for off", minvalue=0.0)
        if choice is not None:
            asyncio.get_running_loop().create_task(self.ember.set_target_temperature(float(choice)))

    def close(self):
        self.root.destroy()


    async def show(self):
        await self.ember.start()
        while True:
            self.battery_percentage_value["text"] = self.ember.battery_percentage
            self.charging_status_value["text"] = f"{self.ember.charging_status_message} ({self.ember.charging_status})"
            self.battery_temperature_value["text"] = '{0:.2f}'.format(self.ember.battery_temperature)
            self.battery_voltage_maybe_value["text"] = self.ember.battery_voltage_maybe
            self.current_temperature_value["text"] = '{0:.2f}'.format(self.ember.current_temperature)
            self.liquid_level_value["text"] = self.ember.liquid_level
            self.liquid_state_value["text"] = f"{self.ember.liquid_state_message} ({self.ember.liquid_state})"
            self.target_temperature_value["text"] = '{0:.2f}'.format(self.ember.target_temperature)
            self.charging_state_value["text"] = self.ember.charging_state

            self.root.update()
            await asyncio.sleep(1)
