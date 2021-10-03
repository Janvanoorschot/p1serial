import asyncio
import re
import datetime


class P1Proto:

    def __init__(self, serialport, p1dbase):
        self.serialport = serialport
        self.p1dbase = p1dbase
        self.lock = asyncio.Lock()
        self.count = 0
        self.linepattern = re.compile("([\\d:\.-]+)(\(.+\))")
        self.valpatterns = {
            "1-0:1.7.0": re.compile("\(([\\d.]+)\*kWh\)"),
            "1-0:1.8.1": re.compile("\(([\\d.]+)\*kWh\)"),
            "1-0:1.8.2": re.compile("\(([\\d.]+)\*kWh\)"),
            "1-0:2.8.1": re.compile("\(([\\d.]+)\*kWh\)"),
            "1-0:2.8.2": re.compile("\(([\\d.]+)\*kWh\)"),
        }

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
                if id in self.valpatterns:
                    msub = self.valpatterns[id].match(val)
                    if msub:
                        result[id] = float(msub.group(1))
        return result

    def handle_msg(self, msg):
        delivtarief1 = msg['1-0:1.8.1']
        delivtarief2 = msg['1-0:1.8.2']
        self.p1dbase.record(datetime.datetime.now(), delivtarief1, delivtarief2)


    async def run(self):
        # yes, two awaits. Why cant Lock start in locked mode?
        await self.lock.acquire()
        await self.lock.acquire()

