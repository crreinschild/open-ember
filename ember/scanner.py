import asyncio
from bleak import BleakScanner, BleakClient, BLEDevice, BleakGATTCharacteristic
from rich.live import Live
from rich.table import Table
from collections import OrderedDict

class Scanner:
    devices = OrderedDict()

    def generate_table(self) -> Table:
        """Make the device table"""
        table = Table(show_header=True, header_style="bold blue")
        table.add_column("Address")
        table.add_column("Name")
        table.add_column("Signal")
        table.add_column("Data")

        for addr,data in self.devices.items():
            #print(data.name)
            table.add_row(f"{addr}", f"{data['name']}", f"{data['rssi']}", f"{data['data']}")

        return table

    # Copied from docs; TODO: implement ability to scan for ember devices
    async def scan(self):
        stop_event = asyncio.Event()

        # TODO: add something that calls stop_event.set()

        def callback(device, advertising_data):
            # TODO: do something with incoming data
            self.devices[device.address] = {"name": device.name, "rssi": advertising_data.rssi, "data": advertising_data}
            #print("Received advertising data")
            #print(advertising_data)
            #print(device)
            #inspect(self.devices)

            pass

        async with BleakScanner(callback) as scanner:
            # ...
            # Important! Wait for an event to trigger stop, otherwise scanner
            # will stop immediately.

            await stop_event.wait()

    async def display(self):
        loop = asyncio.get_running_loop()
        with Live(self.generate_table(), refresh_per_second=4) as live:
            loop.create_task(self.scan())
            while True:
                await asyncio.sleep(0.4)
                live.update(self.generate_table())


#Scanner().display()
asyncio.run(Scanner().display())