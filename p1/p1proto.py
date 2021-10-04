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
        self.valfuncs = {
            "0-0:1.0.0": self.parse_date,
            "1-0:1.8.1": self.parse_kw,
            "1-0:1.8.2": self.parse_kw,
            "1-0:2.8.1": self.parse_kw,
            "1-0:2.8.2": self.parse_kw,
        }
        self.valpatterns = {
            "kw": re.compile("\(([\\d.]+)\*kWh\)"),
            "date": re.compile("\(([\\d]+W)\)"),
        }

    async def timer(self):
        self.count += 1
        block = await self.serialport.read()
        if block != None:
            msg = self.parse_block(block)
            self.handle_msg(msg)

    def stop(self):
        self.lock.release()

    def parse_kw(self, val):
        pattern = self.valpatterns["kw"]
        msub = pattern.match(val)
        if msub:
            datestr = msub.group(1)
            locdate = datetime.datetime.strptime(datestr, "%y%m%d%H%M%S")      # YYMMDDhhmmssX
            return locdate
        else:
            return None

    def parse_date(self, val):
        pattern = self.valpatterns["date"]
        msub = pattern.match(val)
        if msub:
            return float(msub.group(1))
        else:
            return None

    def parse_block(self, block):
        result = {}
        for line in block:
            m = self.linepattern.match(line)
            if m:
                id = m.group(1)
                val = m.group(2)
                if id in self.valfuncs:
                    func = self.valfuncs[id]
                    result[id] = func(val)
        return result

    def handle_msg(self, msg):
        locdate = msg['0-0:1.0.0']
        delivtarief1 = msg['1-0:1.8.1']
        delivtarief2 = msg['1-0:1.8.2']
        self.p1dbase.record(datetime.datetime.now(), locdate, delivtarief1, delivtarief2)

    async def run(self):
        # yes, two awaits. Why cant Lock start in locked mode?
        await self.lock.acquire()
        await self.lock.acquire()
