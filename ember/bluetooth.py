from bleak import BleakScanner, BleakClient, BLEDevice, BleakGATTCharacteristic
import asyncio

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

def charging_status_str(state):
    match state:
        case 0:
            return "Unplugged"
        case 1:
            return "Plugged In"

class Ember:
    def __init__(self):
        # init settings
        self.client = None
        self.battery_percentage = 0
        self.charging_status = 0
        self.charging_status_message = ""
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
                    await self.update_battery()
                case 3:
                    self.charging_state = "Not Charging"
                    await self.update_battery()
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
            self.charging_status_message = charging_status_str(self.charging_status)
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
