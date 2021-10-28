from bluepy.btle import Peripheral, UUID
from bluepy.btle import Scanner, DefaultDelegate
class ScanDelegate(DefaultDelegate):
    def __init__(self):
        DefaultDelegate.__init__(self)
    def handleDiscovery(self, dev, isNewDev, isNewData):
        if isNewDev:
            print("Discovered device", dev.addr)
        elif isNewData:
            print("Received new data from", dev.addr)
            
            
# ---- add ----
class myDelegate(DefaultDelegate):
    def __init__(self):
        DefaultDelegate.__init__(self)
    def handleNotification(self, cHandle, data):
        print("A notification was received: %s"% data)
# -------------
            
scanner = Scanner().withDelegate(ScanDelegate())
devices = scanner.scan(10.0)
n=0
for dev in devices:
    print("%d: Device %s (%s), RSSI=%d dB" % (n, dev.addr, dev.addrType, dev.rssi))
    n += 1
    for (adtype, desc, value) in dev.getScanData():
        print("  %s = %s" % (desc, value))
        
number = input('Enter your device number: ')
number = int(number)
print('Device', number)
# print(type(devices))
print(list(devices)[number].addr)

print("Connecting...")
dev = Peripheral(list(devices)[number].addr, 'random')
# ----- add -----
dev.setDelegate(myDelegate())

print("Services...")
for svc in dev.services:
    print(str(svc))

#----- add -----
enableNotify = False
enableIndicate = True

try:
    testService= dev.getServiceByUUID(UUID(0xfff0))
    for ch in testService.getCharacteristics():
        print(str(ch))
        
    ch = dev.getCharacteristics(uuid=UUID(0xfff1))[0]
    print("ch:", ch)
    print("support:", ch.supportsRead()) 
    if (ch.supportsRead()):
        print(ch.read())
        
    # --------- add CCCD operation --------
    print(ch.valHandle)
    cccd = ch.valHandle + 1
    
    if enableNotify:
        dev.writeCharacteristic(cccd,"\x01\x00") # setup to enable notifications
        print("Enable notifications......")
    if enableIndicate:
        dev.writeCharacteristic(cccd,b"\x02\x00") # setup to enable indications
        print("Enable indications......")
        
    while True:
        if dev.waitForNotifications(1.0):
            # handleNotification() was called
            continue
        print("Waiting")

finally:
    dev.disconnect()
