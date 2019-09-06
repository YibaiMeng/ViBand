#!/usr/bin/python3
import signal
import time
import struct
import threading

import serial

collect_data = True
t = None
do_show_wrong_data = False


def open_connection(dat_queue):
    ser = serial.Serial()
    ser.baudrate = 115200
    ser.port = '/dev/ttyUSB0'
    if not ser.is_open:
        ser.open()
        print("[open_connection] : connection opened!")
    ser.read_until(b'\xff\xff')
    print("[open_connection] : first synv byte appeared!")

    def collect_func():
        while collect_data:
            dat = ser.read_until(b'\xff\xff')  # read(size=500))
            # TODO：when I send 0x0a using fwrite from esp32, the byte get changed into 0x0d0x0a. I have no idea who did it, thesp32, the CP210x USB2UART chip, Linux's uart library or pyserial.
            # It appears that 0xd0x0a get changed also...
            dat = dat.replace(b'\x0d\x0a', b'\x0a')
            if len(dat) != 8:
                if do_show_wrong_data:
                    print("[open_connection]: wrong data, ignored!")
                    print(dat)
                continue
            LSB_sens = 8192  # Range is ±4g
            # Note: h is for short, standard size is 2 bytes. But i don't know if it's true on every system.
            ans = struct.unpack("<4h", dat)
            x = ans[0] / LSB_sens
            y = ans[1] / LSB_sens
            z = ans[2] / LSB_sens
            # print(x,y,z)
            dat_queue.put((x, y, z))
        print("[open_connection]: data retreving stopped!")
        ser.close()
        print("[open_connection]: port closed!")
        return
    global t
    t = threading.Thread(target=collect_func)
    t.start()


def close_connection():
    global collect_data
    collect_data = False
    print("[close_connection]: signal sent!")
    if t:
        t.join()
        print("[close_connection]: thread joined, data retreving stopped!")
    else:
        print("close_connection]: no connection to stop!")
