import tkinter as tk
from tkinter import simpledialog, ttk

from ember.bluetooth import Ember
from ember.scanner import Scanner
import asyncio

class Window(tk.Tk):
    embers = {} # addr -> device

    def __init__(self, loop):
        super().__init__()
        self.loop = loop
        self.root = tk.Tk()

        self.notebook = ttk.Notebook(self.root)


        #self.ember_widgets = #[EmberWidget( notebook, self.ember, loop)]

        #self.ember_widget1 = EmberWidget(self.notebook, self.embers[0])
        #self.ember_widget2 = EmberWidget(self.notebook, self.embers[1])
        #self.notebook.add(self.ember_widget1, text="frame1")
        #self.notebook.add(self.ember_widget2, text="frame2")
        #self.notebook.pack(fill=tk.BOTH, expand=True)

    async def show(self):
        scanner = Scanner()
        asyncio.get_running_loop().create_task(scanner.scan())
        while True:
            # check for bluetooth devices with name 'Ember Ceramic Mug'
            # if there is a device that does not exist in the list, add it and create a tab

            ember_devices = [(addr,data) for (addr,data) in scanner.devices.items() if data['name'] == 'Ember Ceramic Mug']
            for addr,data in ember_devices:
                if addr not in self.embers:
                    ember = Ember(addr)
                    await ember.start()
                    self.embers[addr] = ember
                    self.notebook.add(EmberWidget(self.notebook, self.embers[addr]))
                    self.notebook.pack(fill=tk.BOTH, expand=True)

            self.root.update()
            await asyncio.sleep(1/30)
        #for w in self.ember_widgets:
            #await w.start()

class EmberWidget(ttk.Frame):
    ember: Ember

    def __init__(self, parent, e):
        super().__init__(parent)
        self.parent = parent
        self.ember = e

        self.battery_percentage_label = ttk.Label(self, text="Battery Percentage")
        self.battery_percentage_label.grid(row=0, column=0, padx=(10,10), pady=(10, 10))
        self.battery_percentage_value = ttk.Label(self, text="0")
        self.battery_percentage_value.grid(row=0, column=1, padx=(10,10), pady=(10, 10))
        self.charging_status_label = ttk.Label(self, text="Charging Status")
        self.charging_status_label.grid(row=1, column=0, padx=(10,10), pady=(10, 10))
        self.charging_status_value = ttk.Label(self, text="0")
        self.charging_status_value.grid(row=1, column=1, padx=(10,10), pady=(10, 10))
        self.battery_temperature_label = ttk.Label(self, text="Battery Temperature")
        self.battery_temperature_label.grid(row=2, column=0, padx=(10,10), pady=(10, 10))
        self.battery_temperature_value = ttk.Label(self, text="0")
        self.battery_temperature_value.grid(row=2, column=1, padx=(10,10), pady=(10, 10))
        self.battery_voltage_maybe_label = ttk.Label(self, text="Battery Voltage Maybe")
        self.battery_voltage_maybe_label.grid(row=3, column=0, padx=(10,10), pady=(10, 10))
        self.battery_voltage_maybe_value = ttk.Label(self, text="0")
        self.battery_voltage_maybe_value.grid(row=3, column=1, padx=(10,10), pady=(10, 10))
        self.current_temperature_label = ttk.Label(self, text="Current Temperature")
        self.current_temperature_label.grid(row=4, column=0, padx=(10,10), pady=(10, 10))
        self.current_temperature_value = ttk.Label(self, text="0")
        self.current_temperature_value.grid(row=4, column=1, padx=(10,10), pady=(10, 10))
        self.liquid_level_label = ttk.Label(self, text="Liquid Level")
        self.liquid_level_label.grid(row=5, column=0, padx=(10,10), pady=(10, 10))
        self.liquid_level_value = ttk.Label(self, text="0")
        self.liquid_level_value.grid(row=5, column=1, padx=(10,10), pady=(10, 10))
        self.liquid_state_label = ttk.Label(self, text="Liquid State")
        self.liquid_state_label.grid(row=6, column=0, padx=(10,10), pady=(10, 10))
        self.liquid_state_value = ttk.Label(self, text="0")
        self.liquid_state_value.grid(row=6, column=1, padx=(10,10), pady=(10, 10))
        self.target_temperature_label = ttk.Label(self, text="Target Temperature")
        self.target_temperature_label.grid(row=8, column=0, padx=(10,10), pady=(10, 10))
        self.target_temperature_value = ttk.Label(self, text="0")
        self.target_temperature_value.grid(row=8, column=1, padx=(10,10), pady=(10, 10))
        self.charging_state_label = ttk.Label(self, text="Charging State")
        self.charging_state_label.grid(row=9, column=0, padx=(10,10), pady=(10, 10))
        self.charging_state_value = ttk.Label(self, text="0")
        self.charging_state_value.grid(row=9, column=1, padx=(10,10), pady=(10, 10))
        self.set_temperature_button = ttk.Button(self, text="Set Temperature", command=self.set_temperature)
        self.set_temperature_button.grid(row=10, column=0, padx=(10,10), pady=(10, 10))

    def set_temperature(self):
        choice = simpledialog.askfloat("Choose Temperature", "Choose Temperature, 0 for off", minvalue=0.0)
        if choice is not None:
            asyncio.get_running_loop().create_task(self.ember.set_target_temperature(float(choice)))


    #async def start(self, ember_id = None):
        #await self.ember.start(ember_id)
    #    while True:
    #        self.update()
    #        await asyncio.sleep(1)

    def update(self):
        self.battery_percentage_value["text"] = self.ember.battery_percentage
        self.charging_status_value["text"] = f"{self.ember.charging_status_message} ({self.ember.charging_status})"
        self.battery_temperature_value["text"] = '{0:.2f}'.format(self.ember.battery_temperature)
        self.battery_voltage_maybe_value["text"] = self.ember.battery_voltage_maybe
        self.current_temperature_value["text"] = '{0:.2f}'.format(self.ember.current_temperature)
        self.liquid_level_value["text"] = self.ember.liquid_level
        self.liquid_state_value["text"] = f"{self.ember.liquid_state_message} ({self.ember.liquid_state})"
        self.target_temperature_value["text"] = '{0:.2f}'.format(self.ember.target_temperature)
        self.charging_state_value["text"] = self.ember.charging_state
        self.parent.update()