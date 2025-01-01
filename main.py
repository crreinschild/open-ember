import asyncio
import tkinter as tk
from tkinter import simpledialog
from bleak import BleakScanner, BleakClient, BLEDevice, BleakGATTCharacteristic

def int_to_temp(value):
    return round(value * 0.01, 2)

def liquid_state_str(state):
    match state:
        case 1:
            return "Empty"
        case 2:
            return "Filling"
        case 3:
            return "(Unknown)"
        case 4:
            return "Cooling"
        case 5:
            return "Heating"
        case 6:
            return "Stable Temperature"


class Ember:
    def __init__(self):
        # init settings
        self.client = None
        self.battery_percentage = 0
        self.charging_status = 0
        self.battery_temperature = 0
        self.battery_voltage_maybe = 0
        self.current_temperature = 0
        self.liquid_level = 0
        self.liquid_state = 0
        self.liquid_state_message = ""
        self.target_temperature = 0
        self.charging_state = ""

    async def start(self):
        device = await self.find_ember()
        await self.connect(device)

        await self.update_battery()
        await self.update_current_temperature()
        await self.update_target_temperature()
        await self.update_liquid_level()
        await self.update_liquid_state()

        await self.start_notify()

    async def find_ember(self) -> BLEDevice:
        def callback(device, advertising_data):
            # TODO: do something with incoming data
            print("Received advertising data")
            print(advertising_data)
            print(device)
            pass

        async with BleakScanner(callback) as scanner:
            device = await scanner.find_device_by_name("Ember Ceramic Mug")
            return device

    # Copied from docs; TODO: implement ability to scan for ember devices
    #async def scan(self):
    #    stop_event = asyncio.Event()
#
    #    # TODO: add something that calls stop_event.set()
#
    #    def callback(device, advertising_data):
    #        # TODO: do something with incoming data
    #        print("Received advertising data")
    #        print(advertising_data)
    #        print(device)
    #        pass
#
    #    async with BleakScanner(callback) as scanner:
    #        # ...
    #        # Important! Wait for an event to trigger stop, otherwise scanner
    #        # will stop immediately.
    #        await stop_event.wait()
#
    #    # scanner stops when block exits
    #    # ...

    async def connect(self, addr):
        stop_event = asyncio.Event()
        def callback(sender: BleakGATTCharacteristic, data: bytearray):
            print(f"{sender}: {data}")

        self.client = BleakClient(addr)
        await self.client.connect()
        await self.client.pair()
        print("Connected: " + str(self.client.is_connected))
        services = self.client.services
        for service in services:
            for characteristic in service.characteristics:
                print(f"{characteristic.uuid} {characteristic.description} {characteristic.max_write_without_response_size} {characteristic.properties}")

    async def start_notify(self):
        async def callback(sender: BleakGATTCharacteristic, data: bytearray):
            print(f"{sender}: {data}")
            notify_num = int.from_bytes(data[0:1], byteorder="little")
            match notify_num:
                case 1:
                    await self.update_battery()
                case 2:
                    self.charging_state = "Charging"
                case 3:
                    self.charging_state = "Not Charging"
                case 4:
                    await self.update_target_temperature()
                case 5:
                    await self.update_current_temperature()
                case 6:
                    pass
                case 7:
                    await self.update_liquid_level()
                case 8:
                    await self.update_liquid_state()

        uuid = "fc540012-236c-4c94-8fa9-944a3e5353fa"
        await self.client.start_notify(uuid, callback)

    async def stop_notify(self):
        uuid = "fc540012-236c-4c94-8fa9-944a3e5353fa"
        await self.client.stop_notify(uuid)

    async def disconnect(self):
        await self.client.disconnect()

    async def update_battery(self):
        uuid = "fc540007-236c-4c94-8fa9-944a3e5353fa"
        print("Updating battery status")

        if self.client.is_connected:
            b = await self.client.read_gatt_char(uuid)
            self.battery_percentage = int.from_bytes(b[0:1])
            self.charging_status = bool.from_bytes(b[1:2])
            self.battery_temperature = int_to_temp(int.from_bytes(b[2:4], byteorder="little"))
            self.battery_voltage_maybe = int.from_bytes(b[4:5])

    async def update_current_temperature(self):
        uuid = "fc540002-236c-4c94-8fa9-944a3e5353fa"
        print("Updating current temperature")

        if self.client.is_connected:
            b = await self.client.read_gatt_char(uuid)
            self.current_temperature = int_to_temp(int.from_bytes(b, byteorder="little"))

    async def update_liquid_level(self):
        uuid = "fc540005-236c-4c94-8fa9-944a3e5353fa"
        print("Updating liquid level")

        if self.client.is_connected:
            b = await self.client.read_gatt_char(uuid)
            self.liquid_level = int.from_bytes(b, byteorder="little")

    async def update_liquid_state(self):
        uuid = "fc540008-236c-4c94-8fa9-944a3e5353fa"
        print("Updating liquid state")

        if self.client.is_connected:
            b = await self.client.read_gatt_char(uuid)
            self.liquid_state = int.from_bytes(b, byteorder="little")
            self.liquid_state_message = liquid_state_str(self.liquid_state)

    async def update_target_temperature(self):
        uuid = "fc540003-236c-4c94-8fa9-944a3e5353fa"
        print("Updating target temperature")

        if self.client.is_connected:
            b = await self.client.read_gatt_char(uuid)
            self.target_temperature = int_to_temp(int.from_bytes(b, byteorder="little"))

    async def set_target_temperature(self, target_temperature):
        uuid = "fc540003-236c-4c94-8fa9-944a3e5353fa"

        target_value = target_temperature * 100
        target_int = int(target_value)
        if target_int < 10000:
            target_bytes = target_int.to_bytes(2 , "little")
            print("Setting target temperature to " + str(target_bytes))
            if self.client.is_connected:
                await self.client.write_gatt_char(uuid, target_bytes, response=False)
                await self.update_target_temperature()


class Window(tk.Tk):
    ember = Ember()

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
        liquid_state_message_label = tk.Label(text="Liquid State Message")
        liquid_state_message_label.grid(row=7, column=0, padx=(10,10), pady=(10, 10))
        self.liquid_state_message_value = tk.Label(text="0")
        self.liquid_state_message_value.grid(row=7, column=1, padx=(10,10), pady=(10, 10))
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

        #self.battery_percentage = 0
        #self.charging_status = 0
        #self.battery_temperature = 0
        #self.battery_voltage_maybe = 0
        #self.current_temperature = 0
        #self.liquid_level = 0
        #self.liquid_state = 0
        #self.liquid_state_message = ""
        #self.target_temperature = 0
        #self.charging_state = ""

    def set_temperature(self):
        choice = simpledialog.askfloat("Choose Temperature", "Choose Temperature, 0 for off", minvalue=0.0)
        if choice is not None:
            asyncio.get_event_loop().run_until_complete(self.ember.set_target_temperature(float(choice)))

    def close(self):
        self.loop.call_soon(self.root.destroy)


    async def show(self):
        await self.ember.start()
        while True:
            self.battery_percentage_value["text"] = self.ember.battery_percentage
            self.charging_status_value["text"] = self.ember.charging_status
            self.battery_temperature_value["text"] = '{0:.2f}'.format(self.ember.battery_temperature)
            self.battery_voltage_maybe_value["text"] = self.ember.battery_voltage_maybe
            self.current_temperature_value["text"] = '{0:.2f}'.format(self.ember.current_temperature)
            self.liquid_level_value["text"] = self.ember.liquid_level
            self.liquid_state_value["text"] = self.ember.liquid_state
            self.liquid_state_message_value["text"] = self.ember.liquid_state_message
            self.target_temperature_value["text"] = '{0:.2f}'.format(self.ember.target_temperature)
            self.charging_state_value["text"] = self.ember.charging_state

            self.root.update()
            await asyncio.sleep(1)

class App:
    async def exec(self):
        self.window = Window(asyncio.get_event_loop())
        await self.window.show()

asyncio.run(App().exec())