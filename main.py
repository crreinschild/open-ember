import asyncio
from gui import tkinter

class App:
    window: tkinter.Window

    def __init__(self):
        pass

    async def exec(self):
        self.window = tkinter.Window(asyncio.get_running_loop())
        await self.window.show()

asyncio.run(App().exec())