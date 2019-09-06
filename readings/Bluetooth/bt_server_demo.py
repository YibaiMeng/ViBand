# PyBlueZ
# Installation:
# sudo apt-get install libbluetooth-dev
# sudo apt install bluez
# pip3 install --user pybluez 
# 
# https://github.com/pybluez/pybluez
# simple inquiry example
import bluetooth

nearby_devices = bluetooth.discover_devices(lookup_names=True)
print("found %d devices" % len(nearby_devices))

for addr, name in nearby_devices:
    print("  %s - %s" % (addr, name))
