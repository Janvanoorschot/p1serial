import os
import serial   # pip install pyserial
from datetime import datetime, timedelta
import logging
import time
import re
import sys

ser = serial.Serial()

# DSMR 4.0/4.2 > 115200 8N1:
ser.baudrate = 115200
ser.bytesize = serial.EIGHTBITS
ser.parity = serial.PARITY_NONE
ser.stopbits = serial.STOPBITS_ONE

ser.xonxoff = 0
ser.rtscts = 0
ser.timeout = 12
ser.port = "/dev/ttyUSB0"
ser.close()
i = 0
watt = []
consumption_1 = None
consumption_2 = None
return_1 = None
return_2 = None


def expires(minutes: int = 5):
    future = datetime.now() + timedelta(seconds=minutes*60)
    return int(future.strftime("%s"))


def average(lst):
    return round(int(sum(lst) / len(lst)))


hour_timestamp = expires(60)
five_minutes_timestamp = expires(5)

logging.warning("Start collecting")

while True:
    ser.open()
    checksum_found = False

    while not checksum_found:
        timestamp = int(time.time())

        try:

            ser_data = ser.readline()  # Read in serial line.
            # print(f"here!!!!!!!!!!!!!!!!!!!!!!!!!!!!!{ser_data}")
            # Strip spaces and blank lines
            ser_data = ser_data.decode('ascii').strip()
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            logging.warning(str(e) + " | " + str(exc_type) +
                            " | " + str(fname) + " | " + str(exc_tb.tb_lineno))
            pass

        try:
            if re.match(r'(?=1-0:1.7.0)', ser_data):  # 1-0:1.7.0 = Actual usage in kW
                kw = ser_data[10:-4]  # Knip het kW gedeelte eruit (0000.54)
                # vermengvuldig met 1000 voor conversie naar Watt (540.0) en rond het af
                watt.append(int(float(kw) * 1000))

            if re.match(r'(?=1-0:1.8.1)', ser_data):
                consumption_1 = ser_data[10:-5]

            if re.match(r'(?=1-0:1.8.2)', ser_data):
                consumption_2 = ser_data[10:-5]

            if re.match(r'(?=1-0:2.8.1)', ser_data):
                return_1 = ser_data[10:-5]

            if re.match(r'(?=1-0:2.8.2)', ser_data):
                return_2 = ser_data[10:-5]

            try:
                if watt:
                    if timestamp >= five_minutes_timestamp:
                        avg_watt = average(watt)
                        print(f"avg_watt:[{avg_watt}]")
                        five_minutes_timestamp = expires(5)
                        watt = []

            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                logging.warning(str(e) + " | " + str(exc_type) +
                                " | " + str(fname) + " | " + str(exc_tb.tb_lineno))
                pass

            try:
                if None not in (consumption_1, consumption_2, return_1, return_2):
                    # print(f"{consumption_1}/{consumption_2}/{return_1}/{return_2}/{timestamp}")
                    if timestamp >= hour_timestamp:
                        print(f"{consumption_1}/{consumption_2}/{return_1}/{return_2}/{timestamp}")
                        hour_timestamp = expires(60)
                        consumption_1 = None
                        consumption_2 = None
                        return_1 = None
                        return_2 = None
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                logging.warning(str(e) + " | " + str(exc_type) +
                                " | " + str(fname) + " | " + str(exc_tb.tb_lineno))
                pass

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            logging.warning(str(e) + " | " + str(exc_type) +
                            " | " + str(fname) + " | " + str(exc_tb.tb_lineno))
            pass

        # Check when the exclamation mark is received (end of data)
        if re.match(r'(?=!)', ser_data, 0):
            checksum_found = True

    ser.close()
