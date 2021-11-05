from bluepy.btle import Peripheral, UUID
from bluepy.btle import Scanner, DefaultDelegate
import threading
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
enableNotify = True
enableIndicate = False
#---------------

try:
    #for LED service
    
    LEDService= dev.getServiceByUUID(UUID(0xa002))
    for ch in LEDService.getCharacteristics():
        print(str(ch))
        
    ch2 = dev.getCharacteristics(uuid=UUID(0xa003))[0]
    print("ch:", ch2)
    print("support:", ch2.supportsRead()) 
    if (ch2.supportsRead()):
        print("LED service")
        print(ch2.read())
    
    # for buttonService
    testService= dev.getServiceByUUID(UUID(0xa000))
    for ch in testService.getCharacteristics():
        print(str(ch))
        
    ch = dev.getCharacteristics(uuid=UUID(0xa001))[0]
    print("ch:", ch)
    print("support:", ch.supportsRead()) 
    if (ch.supportsRead()):
        print(ch.read())
    
    #control led2 open and close
    led=0
    def blink(led):
        if led==0:
            ch2.write(bytes("1","utf-8"))
            led=1
        elif led==1:
            ch2.write(bytes("0","utf-8"))
            led=0
        return led
    
    # --------- add CCCD operation --------
    print(ch.valHandle)
    cccd = ch.valHandle + 1
    
    if enableNotify:
        dev.writeCharacteristic(cccd,b"\x01\x00") # setup to enable notifications
        print("Enable notifications......")
    if enableIndicate:
        dev.writeCharacteristic(cccd,b"\x02\x00") # setup to enable indications
        print("Enable indications......")
        
    while True:
        led=blink(led)
        if dev.waitForNotifications(1.0):
            # handleNotification() was called
            continue
        print("Waiting")

finally:
    dev.disconnect()
