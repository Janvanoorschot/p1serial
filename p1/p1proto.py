import asyncio
import re


class P1Proto:

    def __init__(self, serialport, p1dbase):
        self.serialport = serialport
        self.p1dbase = p1dbase
        self.lock = asyncio.Lock()
        self.count = 0
        self.linepattern = re.compile("([\\d:\.-]+)\((.+)\)")

    async def timer(self):
        print(f"timer: {self.count}")
        self.count += 1
        block = await self.serialport.read()
        if block != None:
            msg = self.parse_block(block)
            self.handle_msg(msg)
        if self.count > 10:
            self.lock.release()

    def parse_block(self, block):
        result = {}
        for line in block:
            m = self.linepattern.match(line)
            if m:
                id = m.group(1)
                val = m.group(2)
                print(f"{id}/{val}")
                result[m.group(1)] = m.group(2)
        return result

    def handle_msg(self, msg):
        pass


    async def run(self):
        # yes, two awaits. Why cant Lock start in locked mode?
        await self.lock.acquire()
        await self.lock.acquire()

