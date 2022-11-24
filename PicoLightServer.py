import network
import socket
import time
import random
from neopixel import NeoPixel

NEOPIXEL_PIN = 0
NUMBER_PIXELS = 256
strip = NeoPixel(machine.Pin(NEOPIXEL_PIN), NUMBER_PIXELS)

ssid = 'pi wifi'
password = 'wifipassword'

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(ssid, password)

html = """<!DOCTYPE html>
<html>
    <head> <title>Pico W</title> </head>
    <body> <h1>Pico W</h1>
        <p>%s</p>
         <form action="/light/on" method="get">
            <input type="submit" value="On" />
        </form>
         <form action="/light/toggle" method="get">
            <input type="submit" value="Toggle" />
        </form>
         <form action="/light/off" method="get">
            <input type="submit" value="Off" />
        </form>
        <form>
             <input type="checkbox" id="1" name="1" value="1">
            <input type="checkbox" id="2" name="2" value="2">
            <input type="checkbox" id="vehicle3" name="vehicle3" value="Boat">
            <input type="submit" name="submit" value="Submit">
        </form>
    </body>
</html>
"""

def allOff(strip):
    for each_index in range(256):
        strip[each_index] = (
            0,
            0,
            0
        )
    strip.write()
    

def randomlyLight(strip):
    for each_index in range(256):
        strip[each_index] = (
            random.randint(0,255),
            random.randint(0,255),
            random.randint(0,255)
            )
    strip.write()

max_wait = 10
while max_wait > 0:
    if wlan.status() < 0 or wlan.status() >= 3:
        break
    max_wait -= 1
    print('waiting for connection...')
    time.sleep(1)

if wlan.status() != 3:
    raise RuntimeError('network connection failed')
else:
    print('connected')
    status = wlan.ifconfig()
    print( 'ip = ' + status[0] )

addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]

s = socket.socket()
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(addr)
s.listen(1)

print('listening on', addr)

# Listen for connections
stateis = "LED is UNKNOWN"
while True:
    try:
        cl, addr = s.accept()
        print('\nclient connected from', addr)
        request = cl.recv(1024)
        print(request)

        request = str(request)
        led_on = request.find('/light/on')
        led_off = request.find('/light/off')
        led_toggle = request.find('/light/toggle')
        print( 'led on = ' + str(led_on))
        print( 'led off = ' + str(led_off))
        print( 'led toggle = ' + str(led_toggle))
        
        if led_toggle == 6:
            print(f"led toggle from {stateis}")
            if stateis == "LED is ON":
                allOff(strip)
                stateis = "LED is OFF"
            else:
                randomlyLight(strip)
                stateis = "LED is ON"
        elif led_on == 6:
            print("led on")
            stateis = "LED is ON"
            randomlyLight(strip)
        elif led_off == 6:
            print("led off")
            stateis = "LED is OFF"
            allOff(strip)

        response = html % stateis

        cl.send('HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n')
        cl.send(response)
        cl.close()

    except OSError as e:
        cl.close()
        print('connection closed')