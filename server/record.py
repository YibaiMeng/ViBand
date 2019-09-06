import time
import json

import config
import server
import process

server.start_server()
fp = open("dat_log.json", "a")

print("start in 5")
time.sleep(1)
print("start in 4")
time.sleep(1)
print("start in 3")
time.sleep(1)
print("start in 2")
time.sleep(1)
print("start in 1")
time.sleep(1)

fp.write("[")
start = time.time()
while time.time() - start < 10:    
    json.dump(list(process.spectra), fp)
    fp.write(",\n")
    time.sleep(0.05)
fp.write("]")
fp.close()

print("over!")
