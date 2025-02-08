import asyncio
from gui import tkinter

class App:
    async def exec(self):
        self.window = tkinter.Window(asyncio.get_event_loop())
        await self.window.show()

asyncio.run(App().exec())