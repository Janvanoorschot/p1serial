import asyncio
import concurrent.futures
import serial
import logging
import time
import os
import re

class SerialPort:

    def __init__(self, loop, port):
        self.loop = loop
        self.port = port
        self.ser = serial.Serial()
        # DSMR 4.0/4.2 > 115200 8N1:
        self.ser.baudrate = 115200
        self.ser.bytesize = serial.EIGHTBITS
        self.ser.parity = serial.PARITY_NONE
        self.ser.stopbits = serial.STOPBITS_ONE
        self.ser.xonxoff = 0
        self.ser.rtscts = 0
        self.ser.timeout = 12
        self.ser.port = "/dev/ttyUSB0"
        self.ser.close()

    async def read(self):
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
            res = await self.loop.run_in_executor(executor, self.sync_read)
            if res and len(res) > 3:
                return res
            else:
                return None

    def sync_read(self):
        result = []
        self.ser.open()
        checksum_found = False
        while not checksum_found:
            timestamp = int(time.time())
            try:
                ser_data = self.ser.readline()  # Read in serial line.
                ser_data = ser_data.decode('ascii').strip()
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                logging.warning(str(e) + " | " + str(exc_type) + " | " + str(fname) + " | " + str(exc_tb.tb_lineno))
                ser_data = "!error"
            if re.match(r'(?=!)', ser_data, 0):
                checksum_found = True
            else:
                result.append(ser_data)
        self.ser.close()
        return result



